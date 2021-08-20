import os
from os.path import join, isfile, isdir
from datetime import date
from typing import Iterable
import pandas as pd
from .settings import RAW_PATH

class NoRawDataException(Exception): pass

def vehicle_trace(vehicle_id: str, dates: Iterable[date])->dict:
    """Creates a list of GPS records for a given vehicle for the specified
    *dates*..

    :param vehicle_id: Vehicle ID as archived in the data lake. Correspondence
        between alphanumerical hash and integer ID is in the project database

    :param dates: dates for which we wish to extract data.

    :return: A list of dicts for GPS pings. Each list element is an individual
        GPS ping:

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
    data = []
    for date in dates:
        fldr = join(
            RAW_PATH,
            str(date.month).zfill(2),
            date.strftime("%Y%m%d"))
        if not isdir(fldr):
            continue
        filename = join(fldr, '{}.gzip'.format(vehicle_id))
        if not isfile(filename):
            continue
        data.append(pd.read_csv(filename))
    try:
        df = pd.concat(data)
    except ValueError as e:
        raise NoRawDataException(vehicle_id)
    df.columns=['time', 'speed', 'lon', 'lat', 'heading']
    df = df.assign(type='via', heading_tolerance= 45)
    return df.to_dict('records')
