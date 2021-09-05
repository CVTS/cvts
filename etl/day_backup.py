import sys
import os
import glob
from os.path import join, isdir, basename
from multiprocessing import Pool
import pandas as pd


class backupDayData(object):
    def __init__(self, work_fldr, output_folder, num_workers):
        self.fldr = work_fldr
        self.pool = None
        self.num_workers = num_workers
        self.target_folder = output_folder
        if not isdir(self.target_folder):
            os.mkdir(self.target_folder)

    def backup(self):
        files = list(glob.glob(f'{self.fldr}/*.csv'))
        new_files = [join(self.target_folder, basename(x)) for x in files]

        pool = Pool(processes=self.num_workers, )
        for source, target in zip(files, new_files):
            pool.apply_async(write_down, [source, target])
        pool.close()
        pool.join()


def write_down(file_source, target_file):
    """Writes individual dataframes to disk"""
    df = pd.read_csv(file_source)
    df.to_parquet(target_file.replace('.csv', '.parquet'), compression='brotli', index=False)


if __name__ == '__main__':
    fldr = sys.argv[1]
    output_folder = sys.argv[2]
    num_workers = sys.argv[3]
    mp_class = backupDayData(fldr, output_folder, num_workers)
    mp_class.backup()
