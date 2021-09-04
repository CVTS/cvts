[return to parent](../README.md)


# Convenience Scripts

... mostly useful for dev.


- ***cvts.sh***: Convenience script for setting up environments. I either source
  this from *.bash_aliases* or put it in */etc/profile.d*.

- ***csv2json***: A script for converting a 2017 format CSV to a JSON document that can be fed into
  Valhalla. This is used by *test.sh* in the root of this repository.

- ***json2geojson***: A script for converting the output from Valhalla to a GeoJSON document. This
  is used by *test.sh* in the root of this repository.

- ***launch_tunneled_jupyter_lab.sh***: TODO.

- ***setup-valhalla.sh***: Automation script for building Valhalla. This is pretty specific to the
  state of the world at a particular point in time and will likely need twerking to work at any
other.

- ***start-docker-postgres.sh***: Script for starting a local Postgres instances in docker.

- ***locatebase.py***: Uses the algorithm we use for locating bases against the data in *test.csv*.
