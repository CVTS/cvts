import os
import logging
from os.path import join, isdir
from time import perf_counter
from datetime import datetime
import sys
from day_ingestion import processDayData
from .settings import DATALAKE_DRIVE

logging.basicConfig()
logging.getLogger('sqlalchemy').setLevel(logging.ERROR)


def ingest_month(work_fldr, year, month, files_at_a_time):
    output_folder = join(DATALAKE_DRIVE, f'{year:02}', f'{month:02}')

    days = sorted([x[1] for x in os.walk(work_fldr) if x[1]][0])
    for day in days:
        print('Starting day', datetime.now().strftime("%H:%M:%S"))
        t = perf_counter()
        data_folder = join(work_fldr, day)
        target_folder = join(output_folder, day)
        if not isdir(target_folder):
            os.mkdir(target_folder)
        print(data_folder, target_folder)
        process = processDayData(data_folder, target_folder, files_at_a_time)
        process.process()
        print('     Took: ', round((perf_counter() - t) / 60, 1), 'minutes')


if __name__ == '__main__':
    work_fldr = sys.argv[1]
    year = sys.argv[2]
    month = sys.argv[3]
    files_at_a_time = int(sys.argv[4])
    ingest_month(work_fldr, year, month, files_at_a_time)
