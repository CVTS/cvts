import os
from os.path import join, isfile, isdir
from datetime import datetime
import pandas as pd
from .settings import DATA_LAKE

DAY = 86400

def vehicle_trace(vehicle_id:int, from_instant:int, to_instant:int)->dict:
    """ Creates a list of GPS records for a given vehicle and time interval
        in a format ready to be consumed by Valhala.

    :param int vehicle_id: Vehicle ID as archived in the data lake. Correspondence
                           between alphanumerical hash and integer ID is in the 
                           project database
    :param int from_instant: POSIX time (seconds) for the start of the interval
                             of interest.
    :param int to_instant: POSIX time (seconds) for the end of the interval of
                           of interest.

    :return: A list of dicts for GPS pings. Each list element is an individual 
        GPS ping, and the list is ordered by timestamp:

            {
                'lat':     latitude/y,
                'lon':     longitude/x,
                'time':    datetime,
                'heading': heading,
                'speed':   speed,
                'heading_tolerance': 45,
                'type':    'via'
            }
    """
    dates = [datetime.fromtimestamp(epochtime) for epochtime in range(from_instant, to_instant + DAY, DAY)]
    data = []
    for date in dates:
        fldr = join(DATA_LAKE, str(date.year), str(date.month).zfill(2), datetime.strftime(date, "%Y%m%d"))
        if not isdir(fldr):
            continue
        file = join(fldr, f'vehicle_{vehicle_id}.gzip')
        if not isfile(file):
            continue
        data.append(pd.read_csv(file))
    df = pd.concat(data)
    df = df.loc[(df.datetime>=from_instant)&(df.datetime<=to_instant), :]
    df.sort_values(['datetime'], inplace=True)
    df.columns=['time', 'speed', 'lon', 'lat','heading']
    df = df.assign(type='via', heading_tolerance= 45)
    return df.to_dict('records')