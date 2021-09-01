import os
from os.path import join, isfile, isdir
from datetime import date
from typing import Iterable
import pandas as pd
from sqlalchemy import create_engine

DATALAKE_CONNECTION_STRING = os.environ['DATALAKE_CONNECTION_STRING']
RAW_PATH = os.environ['DATALAKE_RAW_PATH']

class NoRawDataException(Exception): pass


def list_of_vehicles() -> pd.DataFrame:
    """Queries the infrastructure for a table with all vehicles for which we have data to analyze

    :return: A Pandas DataFrame with all vehicles we have in the database
    """
    engine = create_engine(DATALAKE_CONNECTION_STRING)
    conn = engine.connect()

    sql = 'select * from vehicles veh join vehicle_types vt on (veh.vehicle_type_id=vt.id)'
    return pd.read_sql(sql, conn)


def vehicle_trace(vehicle_id: str, dates: Iterable[date]) -> dict:
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
    data_month = {}
    for date in dates:
        fldr_month = join(RAW_PATH, str(date.month).zfill(2))
        if not isdir(fldr_month):
            continue
        filename = join(fldr_month, 'vehicle_{}.zip'.format(vehicle_id))
        if not isfile(filename):
            continue
        if fldr_month not in data_month:
            data_month[fldr_month] = pd.read_csv(filename)

        df = data_month[fldr_month]
        data.append(df[pd.to_datetime(df.datetime, unit='s').dt.date == date])
    try:
        df = pd.concat(data)
    except ValueError as e:
        raise NoRawDataException(vehicle_id)
    df.columns = ['time', 'speed', 'lon', 'lat', 'heading']
    df = df.assign(type='via', heading_tolerance=45)
    return df.to_dict('records')
