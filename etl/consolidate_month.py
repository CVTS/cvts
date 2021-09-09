import os
from os.path import join, isdir, isfile
from multiprocessing import Pool, cpu_count
from datetime import datetime
import pandas as pd
from shapely.geometry import Polygon
import geopandas as gpd
from sqlalchemy import create_engine
from time import perf_counter
from .settings import CONNECTION_STRING, DATALAKE_DRIVE

engine = create_engine(CONNECTION_STRING)


class ConsolidateWholeMonth(object):
    def __init__(self, month):
        self.pool = None
        self.num_workers = cpu_count()
        self.month = month
        conn = engine.connect()
        self.vehicle_ids = [x[0] for x in conn.execute('Select vehicle_id from vehicles')]
        conn.close()
        print(f'{len(self.vehicle_ids)} vehicles found in the database')

    def consolidate(self):
        print(f'consolidating {self.month}')
        pool = Pool(processes=self.num_workers, )
        t = perf_counter()
        for vehicle_id in self.vehicle_ids:
            pool.apply_async(consolidate_vehicle_data, [vehicle_id, self.month])
        pool.close()
        pool.join()
        print('     Took: ', round((perf_counter() - t) / 60, 1), 'minutes')


def consolidate_vehicle_data(vehicle_id, month, year=2020):
    # print(month, vehicle_id)
    pth = f'{DATALAKE_DRIVE}{year}/{month:02}'
    veh_name = f'vehicle_{vehicle_id}.gzip'
    dfs = []
    file_names = []
    stats = []
    for i in range(1, 32):
        fldr = join(pth, f'{year}{month:02}{i:02}')
        if not isdir(fldr):
            continue
        fl = join(fldr, veh_name)

        if isfile(fl):
            df = pd.read_csv(fl).dropna()
            if df.shape[0] == 0:
                os.unlink(fl)
                continue
            min_time = datetime.fromtimestamp(df.datetime.values[0])
            max_time = datetime.fromtimestamp(df.datetime.values[-1])
            xmin = df.x.min()
            xmax = df.x.max()
            ymin = df.y.min()
            ymax = df.y.max()
            box = Polygon([(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax), (xmin, ymin)])
            data = [vehicle_id, min_time.date(), df.shape[0], min_time, max_time, box]
            stats.append(data)
            dfs.append(df)
            file_names.append(fl)
    if len(dfs) == 0:
        return

    # Save the consolidated file
    target_file = join(pth, f'vehicle_{vehicle_id}.zip')
    df = pd.concat(dfs).sort_values('datetime').reset_index(drop=True)
    df.to_csv(target_file, index=False)

    df2 = pd.read_csv(target_file)
    if not df2.shape[0] == df.shape[0]:
        os.unlink(target_file)
        return

    # Save the stats to the database
    stats = gpd.GeoDataFrame(stats, columns=['vehicle_id', 'day', 'pings', 'min_time', 'max_time', 'geom'],
                             geometry='geom').set_crs(4326)
    stats.to_postgis('vehicle_days', engine, if_exists='append')

    # remove the original day-based files
    for fl in file_names:
        os.unlink(fl)