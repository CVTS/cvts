# these are also 'for export'

from ._intersect import points_to_polys
from ._shapes import read_shapefile
from ._utils import (
    DataLakeError,
    distance,
    rawfiles2jsonchunks,
    mongodoc2jsonchunks,
    rawfiles2jsonfile,
    json2geojson,
    jsonfile2geojsonfile)
from .settings import RawDataFormat, RAW_DATA_FORMAT

if RAW_DATA_FORMAT == RawDataFormat.GZIP:
    # do this conditionally because it will fail if certain environment
    # variables aren't set and we don't want to insist they are
    from ._data_retrieval import (
        NoRawDataException,
        list_of_vehicles,
        vehicle_trace)

    def vehicle_ids():
        try:
            return [int(i) for i in list_of_vehicles()['vehicle_id'].values]
        except NoRawDataException:
            raise
        except Exception as e:
            raise DataLakeError(e)

if RAW_DATA_FORMAT == RawDataFormat.CSV:
    from ._utils import gather_input_descriptors as vehicle_ids
    class NoRawDataException(Exception): pass
