#!/bin/bash

#------------------------------------------------------------------------------
# Script for installing data for Vietnam and running a test 'snap'.
#------------------------------------------------------------------------------

[ ! -d venv ] && make venv
. venv/bin/activate

# so valhalla can find its libraries
export LD_LIBRARY_PATH=/usr/local/lib

# for this we still want to use the source (not installed) version
export PYTHONPATH=`pwd`

# stop cvts from checking some things
export CVTS_INITIAL_SETUP_AND_TEST=1

# export CVTS env variables
eval `python cvts/settings.py`

# change to the config directory
pushd "$CVTS_CONFIG_PATH"

# get data for Vietnam
wget https://download.geofabrik.de/asia/vietnam-latest.osm.pbf

# get the config and setup
mkdir -p valhalla_tiles
valhalla_build_config \
    --service-limits-trace-max-distance 10000000 \
    --service-limits-trace-max-shape 1000000 \
    --mjolnir-tile-dir ${PWD}/valhalla_tiles \
    --mjolnir-include-driveways False \
    --mjolnir-include-bicycle False \
    --mjolnir-include-pedestrian False \
    --mjolnir-tile-extract ${PWD}/valhalla_tiles.tar \
    --mjolnir-timezone ${PWD}/valhalla_tiles/timezones.sqlite \
    --mjolnir-admin ${PWD}/valhalla_tiles/admins.sqlite > "$CVTS_VALHALLA_CONFIG_FILE"

# build routing tiles
valhalla_build_tiles -c valhalla.json vietnam-latest.osm.pbf

# tar it up for running the server
find valhalla_tiles | sort -n | tar cf valhalla_tiles.tar --no-recursion -T -

# dump the edges and stuff
valhalla_osm_network valhalla.json > vietnam-network.json

# go to the test directory
popd; pushd test

# convert the test CSV data to JSON
../bin/csv2json test.csv test.json 0

# and produce some output
valhalla_service "$CVTS_VALHALLA_CONFIG_FILE" trace_attributes test.json > snap.json

# and turn this into geojson
../bin/json2geojson snap.json snap.geojson
