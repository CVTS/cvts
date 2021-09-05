import sys
from os.path import isdir, join
from pathlib import Path
from multiprocessing import cpu_count
from day_backup import backupDayData
from .settings import BACKUP_DRIVE


def compress_month_data(source_data: str, year: int, month: int) -> None:
    """Compresses the raw CSV data for an entire month for backup.

    Assumes that there are individual directories for each day inside the
    *source_data* folder.  Also assumes that each folder name is in the format
    YYYYMMDD.

    :param source_data: Directory for the month's data

    :param year: Year of the data being processed (YYYY)

    :param month: Month of the data being processed
    """

    to_folder = join(BACKUP_DRIVE, f'{year}{month:02}')
    Path(to_folder).mkdir(exist_ok=True, parents=True)

    num_workers = cpu_count()

    for day in range(1, 32):
        input_day = join(source_data, f"{year}{month:02}{day:02}")
        if not isdir(input_day):
            print(f'\nData for : {input_day}  does not exist')
            continue
        print(f'\nProcessing day: {input_day}')
        output_day = join(to_folder, f"{year}{month:02}{day:02}")
        Path(output_day).mkdir(exist_ok=True, parents=True)
        mp_class = backupDayData(input_day, output_day, num_workers)
        mp_class.backup()


if __name__ == '__main__':
    source_data = sys.argv[1]
    year = int(sys.argv[2])
    month = int(sys.argv[3])
    compress_month_data(source_data, year, month)
