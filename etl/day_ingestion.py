import os
import sys
import logging
import shutil
from datetime import datetime
from multiprocessing import Pool, cpu_count
from os.path import join, isfile
import pandas as pd
from sqlalchemy import create_engine
from .settings import CONNECTION_STRING

logging.basicConfig()
logging.getLogger('sqlalchemy').setLevel(logging.ERROR)


class processDayData(object):
    def __init__(self, work_fldr, output_folder, files_at_a_time):
        self.fldr = work_fldr
        self.target_folder = output_folder
        self.fal = files_at_a_time
        self.pool = None
        self.num_workers = cpu_count()

        # Holds the information on the correspondence between the vehicle IDs in the original data
        # And the integers we are using to identify the vehicles in our processing
        self.engine = create_engine(CONNECTION_STRING, echo=True)
        self.conn = self.engine.connect()

        self.dfs = {}
        self.df = []

    def process(self):
        if self.check_done():
            return

        # It cleans the output folder in case it crashed in the middle
        shutil.rmtree(self.target_folder)
        os.makedirs(self.target_folder)

        # List all files and separate them into the chunks we will run at a time
        file_list = sorted([x for x in os.walk(self.fldr) if x[2]][0][2])
        parquet_sets = [file_list[i:i + self.fal] for i in range(0, len(file_list), self.fal)]

        for i, set_of_data in enumerate(parquet_sets):
            self.read_data(set_of_data)
            self.load()

        if parquet_sets:
            self.conn.execute('Insert into days_ingested(day, ingestion_date) VALUES(?,?)',
                              [self.fldr.split('/')[-1], datetime.now()])

    def check_done(self) -> bool:
        day = self.fldr.split('/')[-1]
        tot = [x[0] for x in self.conn.execute('Select count(*) from days_ingested where day=?', [day])][0]
        if tot:
            print(f'Day {day} already processed. Skipping')
            return True
        return False

    def read_data(self, set_of_data):
        """Reads the batch of CSV files we will process at once"""
        print(f'    Loading {len(set_of_data)} data files')
        self.df = pd.concat([pd.read_parquet(join(self.fldr, fl)) for fl in set_of_data])
        print(f'    Loaded {self.df.shape[0]:,} records')

    def load(self):
        # Loads the IDs and types we already have in memory
        veh_idx = pd.read_sql('Select * from vehicles', self.engine).set_index('vehicle_id_string')
        veh_types = pd.read_sql('Select * from vehicle_types', self.engine).set_index('').set_index('type_vn')
        veh_types = veh_types['id'].to_dict()
        self.dfs = {veh_str: x for veh_str, x in self.df.groupby(self.df['vehicle'])}
        del self.df

        pool = Pool(processes=self.num_workers, )
        for veh_str, df in self.dfs.items():
            veh_id = veh_idx.at[veh_str, 'vehicle_id'] if veh_str in veh_idx.index else None
            veh_type_db = veh_idx.at[veh_str, 'vehicle_type_id'] if veh_str in veh_idx.index else None
            pool.apply_async(write_down, [df, veh_id, veh_type_db, veh_types, self.target_folder])
        pool.close()
        pool.join()
        self.dfs.clear()


def write_down(df: pd.DataFrame, veh_id: int, veh_type_db: int, veh_types: dict, target_folder: str):
    """Writes individual dataframes to disk"""

    veh_id_str = df.vehicle.values[0]
    conn = None

    # Determines vehicle type:
    veh_int_types = [veh_types.get(vt) for vt in df.VehicleType.unique()]

    if None in veh_int_types:
        # We found a new vehicle type
        engine = create_engine(CONNECTION_STRING, echo=True)
        conn = engine.connect()
        for vt in df.VehicleType.unique():
            if veh_types.get(vt) is None:
                conn.execute('Insert into vehicle_types(type_vn) VALUES(?)', [vt])
                # Doing it in order ensures we get the latest one that appears int he data
                veh_type = conn.execute('select id from vehicle_types where type_vn=?', [vt]).fetchone()[0]
    else:
        veh_type = max(max(veh_int_types), 1)

    # The vehicle type is the maximum, because is can be either unclassified or have an actual classification
    # And the unclassified vehicle is the one with the lowest ID on the vehicle types table

    if veh_id is None:
        # We add the new vehicle to the database and retrieve its ID
        if conn is None:
            engine = create_engine(CONNECTION_STRING, echo=True)
            conn = engine.connect()

        conn.execute('Insert into vehicles(vehicle_id_string, vehicle_type_id) VALUES(?, ?)', [veh_id_str, veh_type])
        veh_id = conn.execute('select vehicle_id from vehicles where vehicle_id_string=?', [veh_id_str]).fetchone()[0]
    else:
        if veh_type > veh_type_db:
            # If the vehicle already existed, we compare the vehicle types to see if we need to update in the database
            if conn is None:
                engine = create_engine(CONNECTION_STRING, echo=True)
                conn = engine.connect()
            conn.execute('Update vehicles set vehicle_type_id=? where vehicle_id_string=?', [veh_type, veh_id_str])

    df.drop(columns=['VehicleType', 'vehicle'], inplace=True)
    fl = join(target_folder, f'vehicle_{veh_id}.gzip')
    df.to_csv(fl, mode='a', index=False, header=not isfile(fl))


if __name__ == '__main__':
    fldr = sys.argv[1]
    output_folder = sys.argv[2]
    files_at_a_time = sys.argv[3]
    database_connection_string = sys.argv[5]

    mp_class = processDayData(fldr, output_folder, 12)
    mp_class.process()
