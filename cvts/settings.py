import os
import logging
from enum import Enum
from datetime import datetime as dt

class RawDataFormat(Enum):
    CSV   = 1
    MONGO = 2
    GZIP  = 3

def _bool_from_env(ev):
    return os.environ.get(ev, 'False') not in ('0', 'False', 'false')

#: Are we debugging. Can be set via the environment variable *CVTS_DEBUG*.
DEBUG = _bool_from_env('CVTS_DEBUG')

_building = _bool_from_env('BUILDING_CVTS_DOC')
_initial_setup_and_test = _bool_from_env('CVTS_INITIAL_SETUP_AND_TEST')

if _building:
    # Sphinx puts the path in the documentation... so make it the default.
    # if we don't do it here, it gets expanded when setting WORK_PATH below.
    os.environ['CVTS_WORK_PATH'] = '~/.cvts'

    #---------------------------------------------------------------------------
    #                            *****IMPORTANT*****
    # Set these to None because they may contain passwords.
    #---------------------------------------------------------------------------
    os.environ.pop('CVTS_MONGO_CONNECTION_STRING', None)
    os.environ.pop('CVTS_POSTGRES_CONNECTION_STRING', None)

#: The connections string for MongoDB. If present, raw data is read from this
#: DB. Read from the environment variable *CVTS_MONGO_CONNECTION_STRING*.
MONGO_CONNECTION_STRING = None

#: The connections string for PostGRE. Read from the environment variable
#: *CVTS_POSTGRES_CONNECTION_STRING*.
POSTGRES_CONNECTION_STRING = os.environ.get('CVTS_POSTGRES_CONNECTION_STRING', None)

_raw_format = os.environ.get('CVTS_RAW_DATA_FORMAT', 'GZIP').upper()

#: The format the raw data is stored in.
RAW_DATA_FORMAT = RawDataFormat.MONGO if _raw_format == 'MONGO' else \
    RawDataFormat.GZIP if _raw_format == 'GZIP' else RawDataFormat.CSV

# check consistency of input data specs
if RAW_DATA_FORMAT == RawDataFormat.MONGO \
        and MONGO_CONNECTION_STRING is None:
    raise Exception(
        'raw data specified to be MONGO but ' \
        'CVTS_MONGO_CONNECTION_STRING not specified.')

#: Are we reading raw data from MongoDB. ``True`` if the environment variable
#: *MONGO_CONNECTION_STRING* is set.
RAW_FROM_MONGO = RAW_DATA_FORMAT == RawDataFormat.MONGO

#: Extensions for the input files to keep. Only used if *RAW_DATA_FORMAT* is
#: *RawDataFormat.CSV* or *RawDataFormat.GZIP*.
RAW_DATA_FILE_EXTENSIONS = ['.csv'] if RAW_DATA_FORMAT == RawDataFormat.CSV \
    else ['.gzip'] if RAW_DATA_FORMAT == RawDataFormat.GZIP else None

_raw_dir_must_exist = RAW_DATA_FORMAT in \
    (RawDataFormat.CSV, RawDataFormat.GZIP) and \
    not (_building or _initial_setup_and_test)

#: The collections to limit ourselves to in the MongoDB.
MONGO_COLLECTION_NAMES = None

#! The number of documents to process if in DEBUG mode.
DEBUG_DOC_LIMIT   = 10

#: The minimum time a vehicle must not move for to be considered 'stopped' in
#: seconds.
MIN_STOP_TIME     = 8 * 60

#: The minimum speed a vehicle can be moving to be considered 'moving' in
#: kilometers per hour.
MIN_MOVING_SPEED  = 4

#: The minimum distance a vehicle can move between two (potentially non-adjacent)
#: GPS points to not be considered 'moving' in meters.
MIN_MOVE_DISTANCE = 50

#: The distance between two stops below which they are considered to be the same
#: location.
MIN_DISTANCE_BETWEEN_STOPS = 50

#: Radius of the Earth in meters.
EARTH_RADIUS      = 6371000

def _get_path(var, must_exist=False):
    if var == 'raw' and RAW_DATA_FORMAT == RawDataFormat.GZIP:
        return os.environ.get('DATALAKE_RAW_PATH', '')

    path = os.environ.get(
        'CVTS_{}_PATH'.format(var.upper()),
        os.path.join(WORK_PATH, var))

    if not _building:
        if path.startswith('~'):
            path = os.path.expanduser(path)

        path = os.path.abspath(os.path.realpath(path))

    if must_exist and not os.path.isdir(path):
        raise Exception('raw data directory ({}) does not exist'.format(path))

    return path

#: Default root directory
WORK_PATH       = os.environ.get(
    'CVTS_WORK_PATH', os.path.join(os.path.expanduser("~"), '.cvts'))

#: Root directory for :doc:`input files<input>`.
RAW_PATH        = _get_path('raw', _raw_dir_must_exist)

#: Root directory for anonymized :doc:`input files<input>`. These are generated
#: by the script
ANON_RAW_PATH   = _get_path('anon_raw')

#: Directory for shape files for :term:`geographies<geography>`.
BOUNDARIES_PATH = _get_path('boundaries')

#: Directory containing :py:data:`VALHALLA_CONFIG_FILE`
CONFIG_PATH     = _get_path('config')

#: Root directory for outputs.
OUT_PATH        = _get_path('output')

#: Output directory for :ref:`trip outputs<trip-output>`.
SEQ_PATH        = os.path.join(OUT_PATH, 'seq')

#: Output directory for :ref:`stop points<stop-points-output>`.
STOP_PATH       = os.path.join(OUT_PATH, 'stop')

#: Output directory for :ref:`source/destination outputs<stop-dest-output>`.
SRC_DEST_PATH   = os.path.join(OUT_PATH, 'src_dest')

#: Output directory for :ref:`speed outputs<speed-output>`.
SPEED_PATH      = os.path.join(OUT_PATH, 'speed')

#: Path to Valhalla configuration file.
VALHALLA_CONFIG_FILE = os.path.join(CONFIG_PATH, 'valhalla.json')

if not _building:
    for p in (CONFIG_PATH, OUT_PATH, SEQ_PATH, STOP_PATH, SRC_DEST_PATH, SPEED_PATH):
        if not os.path.exists(p):
            os.makedirs(p)

# basic logging setup
def setup_logging(level=logging.DEBUG if DEBUG else logging.INFO):
    logging.basicConfig(level=level)
    fileHandler = logging.FileHandler(os.path.join(OUT_PATH, "run-{}.log".format(
        dt.now().isoformat().replace(':', '-').replace('.', '-'))))
    rootLogger = logging.getLogger()
    rootLogger.addHandler(fileHandler)

if __name__ == '__main__':
    # this won't work on windows
    print(';'.join('export CVTS_{}={}'.format(v, eval(v)) for v in (
        'WORK_PATH',
        'RAW_PATH',
        'ANON_RAW_PATH',
        'BOUNDARIES_PATH',
        'CONFIG_PATH',
        'OUT_PATH',
        'SEQ_PATH',
        'STOP_PATH',
        'SRC_DEST_PATH',
        'SPEED_PATH',
        'VALHALLA_CONFIG_FILE')) + ';CVTS_RAW_DATA_FORMAT=' + _raw_format)
