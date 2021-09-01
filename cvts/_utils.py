import os
import csv
import json
from math import sqrt, radians, cos
from typing import Dict, Any, Generator, Union, Iterable
from functools import reduce
from datetime import date
from collections import defaultdict
from ._polyline import decode
from ._base_locator import locate_base
from .settings import (
    MIN_STOP_TIME,
    MIN_MOVING_SPEED,
    MIN_MOVE_DISTANCE,
    EARTH_RADIUS,
    RAW_PATH,
    RAW_DATA_FORMAT,
    RAW_DATA_FILE_EXTENSIONS,
    RawDataFormat)

if RAW_DATA_FORMAT == RawDataFormat.GZIP:
    from ._data_retrieval import (
        vehicle_trace as _do_load_gzips,
        NoRawDataException)

    def _load_gzips(*args, **kwargs):
        try:
            return _do_load_gzips(*args, **kwargs)
        except NoRawDataException:
            raise
        except Exception as e:
            raise DataLakeError(e)



class DataLakeError(Exception): pass



def distance(x0, y0, x1, y1):
    """Quick and adequate distance calculation for for small distances in meters
    between two lon/lats.

    This should be adequate for the purpose of measuring points between points
    in the kinds of GPS traces we are working with, where the typical sampling
    interval is around 15 seconds (i.e., differences in latitude between *y0*
    and *y1* are (very) small).

    :param float x0: First longitude.
    :param float y0: First latitude.
    :param float x1: Second longitude.
    :param float y1: Second latitude.

    :return: Approximate distance between the two points in meters.
    """

    yd = radians(y1 - y0)
    xd = radians(x1 - x0) * cos(radians(y0) + .5*yd)
    return EARTH_RADIUS * sqrt(yd*yd + xd*xd)



def _trip_slices(locs):
    """Generator over sequential slices of *locs* that form trips."""

    if len(locs) == 0:
        yield locs

    else:
        getter = lambda l: (l['time'], l['speed'], l['lat'], l['lon'], l)
        zi = (getter(l) for l in locs)
        last_moved_time, _, ly, lx, loc = next(zi)
        next_chunk        = [loc]
        stationary_points = []

        for t, s, y, x, loc in zi:
            has_moved = s > MIN_MOVING_SPEED or distance(lx, ly, x, y) > MIN_MOVE_DISTANCE

            if has_moved:
                if t - last_moved_time > MIN_STOP_TIME:
                    nsp = len(stationary_points)
                    if nsp > 0:
                        next_chunk.append(stationary_points[0])
                        yield nsp, next_chunk
                        next_chunk = [stationary_points[-1], loc]

                    else:
                        yield nsp, next_chunk
                        next_chunk = [loc]

                else:
                    next_chunk.append(loc)

                del stationary_points[:]
                lx, ly, last_moved_time = x, y, t

            else:
                stationary_points.append(loc)

        if len(next_chunk):
            nsp = len(stationary_points)
            if nsp > 0:
                next_chunk.append(stationary_points[0])
            yield nsp, next_chunk



def _loadcsv(csvfile):
    """Load a raw GeoJSON file and start preparing it for input into Valhalla
    (preparation is finalissed in :py:func:`_prepjson`)."""

    with open(csvfile, 'r') as cf:
        reader = csv.DictReader(cf)
        return [{
            # yes, Longitude and Latitude are back to front.
            'lat': float(row['Longitude']),
            'lon': float(row['Latitude']),
            'time': float(row['Time']),
            'heading': float(row['Orientation']),
            'speed': float(row['speed']),
            'heading_tolerance': 45,
            'type': 'via'} for row in reader]



def _prepjson(locs, split_trips):
    """Finish preparing data for input into Valhalla and return the results as a
    generator over trip(s)."""

    locs.sort(key=lambda l: l['time'])
    if split_trips:
        for n_stationary, clocs in _trip_slices(locs):
            if len(clocs) == 0:
                continue
            clocs[0]['type'] = 'break'
            clocs[-1]['type'] = 'break'
            yield n_stationary, {'shape': clocs, 'costing': 'auto', 'shape_match': 'map_snap'}

    else:
        locs[0]['type'] = 'break'
        locs[-1]['type'] = 'break'
        yield 0, {'shape': locs, 'costing': 'auto', 'shape_match': 'map_snap'}



def mongodoc2jsonchunks(
        doc: Dict[str, Any],
        split_trips: bool) -> Generator[Dict[str, Any], None, None]:
    """Create a generator over all the data for a single vehicle from data in a
    CSV or iterable of CSVs.

    :param doc: A document containing all the documents (each containing a
        GPS point) for a vehicle.

    :param split_trips: if `True`, then split into :term:`trips<trip>`,
        otherwise return all points as a single 'trip'.

    :return: A geenerator over a dicts that contain information about each GPS
        point. Each dict looks like::

            {
                'lat':     doc['y'],
                'lon':     doc['x'],
                'time':    doc['datetime'],
                'heading': doc['heading'],
                'speed':   doc['speed'],
                'heading_tolerance': 45,
                'type':    'via'
            }
    """

    raw_locs = [{
        'lat': d['y'],
        'lon': d['x'],
        'time': d['datetime'],
        'heading': d['heading'],
        'speed': d['speed'],
        'heading_tolerance': 45,
        'type': 'via'} for d in doc]

    base = locate_base(
        [ll['lon'] for ll in raw_locs],
        [ll['lat'] for ll in raw_locs],
        [ll['speed'] for ll in raw_locs])

    return base, _prepjson(raw_locs, split_trips)



def gather_input_descriptors():
    input_files = defaultdict(list) if RAW_DATA_FORMAT == RawDataFormat.CSV \
        else set()
    for root, dirs, files in os.walk(RAW_PATH):
        for f in files:
            rego, ext = os.path.splitext(f)
            if ext in RAW_DATA_FILE_EXTENSIONS:
                if RAW_DATA_FORMAT == RawDataFormat.CSV:
                    input_files[rego].append(os.path.join(root, f))
                else:
                    input_files.add(rego)

    return input_files



def rawfiles2jsonchunks(
        input_descriptor: Union[str, Iterable[str]],
        split_trips: bool,
        dates: Iterable[date]) -> Generator[Dict[str, Any], None, None]:
    """Create a generator over all the data for a single vehicle from data in a
    csv or iterable of csvs.

    :param input_descriptor: Either the name of a
        :ref:`GPS data<gps-data>` file or an iterable of names of such files.

    :param split_trips: if `True`, then split into :term:`trips<trip>`,
        otherwise return all points as a single 'trip'.

    :return: A geenerator over a dicts that contain information about each GPS
        point. Each dict looks like::

            {
                'lat':     float(row['Longitude']),
                'lon':     float(row['Latitude']),
                'time':    float(row['Time']),
                'heading': float(row['Orientation']),
                'speed':   float(row['speed']),
                'heading_tolerance': 45,
                'type':    'via'
            }
    """
    if RAW_DATA_FORMAT == RawDataFormat.CSV:
        if isinstance(input_descriptor, str):
            raw_locs = _loadcsv(input_descriptor)

        elif dates is None:
            raw_locs = reduce(lambda a, b: a + _loadcsv(b), input_descriptor, [])

        else:
            date_strs = [d.strftime('%Y%m%d') for d in dates]
            fls = [f for f in input_descriptor if \
                os.path.split(os.path.dirname(f))[-1] in date_strs]
            raw_locs = reduce(lambda a, b: a + _loadcsv(b), fls, [])

    elif RAW_DATA_FORMAT == RawDataFormat.GZIP:
        if not (isinstance(input_descriptor, str) or isinstance(input_descriptor, int)):
            raise Exception('rawfiles2jsonchunks can only accept or int ' \
                'for argument input_descriptor when loading from gzip, ' \
                'got: {}'.format(type(input_descriptor).__name__))

        raw_locs = _load_gzips(str(input_descriptor), dates)

    base = locate_base(
        [ll['lon'] for ll in raw_locs],
        [ll['lat'] for ll in raw_locs],
        [ll['speed'] for ll in raw_locs])

    return base, _prepjson(raw_locs, split_trips)



def rawfiles2jsonfile(
        csv_file: Union[str, Iterable[str]],
        out_file: str):
    """Call :py:func:`rawfiles2jsonchunks`, passing *csv_files* and *False*, and
    write the result to *out_file*.

    :param csv_file: Either the name of a
        :ref:`GPS data<gps-data>` file or an iterable of names of such files.

    :param out_file: The path of the file to write the trip to.
    """

    _, chunks = rawfiles2jsonchunks(csv_file, False, None)
    with open(out_file, 'w') as jf:
        json.dump(next(chunks)[1], jf, indent=4)



def json2geojson(
        data: Dict[str, Any],
        shape_only: bool) -> Dict[str, Any]:
    """Convert the output from Valhalla to a GeoJSON object.

    On the command line, the call would look like::

        valhalla_service <config-file> trace_attributes <input-file>

    :param data: Output of a call to Valhalla (as described above).

    :param shape_only: Should the returned GeoJSON only include the *shape*
        element from *data*?

    :return: TODO
    """

    shape = [{
        'type': 'Feature',
        'geometry': {
            'type': 'LineString',
            'coordinates': [[p[0]/10., p[1]/10.] for p in decode(data['shape'])]}}]

    if shape_only:
        return {'type': 'FeatureCollection', 'features': shape}

    else:
        edges = data['edges']

        def _point_feature(matched_point, index):
            lat = matched_point.pop('lat')
            lon = matched_point.pop('lon')

            edge_index = matched_point.get('edge_index')
            matched_point['point_index'] = index
            if edge_index is not None:
                names = ', '.join(edges[edge_index].get("names", ["NA"]))
                matched_point['osmnames'] = names
                matched_point['way_id'] = edges[edge_index].get("way_id", "NA")

            return {
                'type': 'Feature',
                'properties': matched_point,
                'geometry': {
                    'type': 'Point',
                    'coordinates': [lon, lat]}}

    return {
        'type': 'FeatureCollection',
        'features': [_point_feature(mp, i) for i, mp in \
                enumerate(data['matched_points'])] + shape}



def jsonfile2geojsonfile(infile, outfile):
    with open(infile, 'r') as jf, open(outfile, 'w') as gf:
        json.dump(json2geojson(json.load(jf), False), gf, indent=4)
