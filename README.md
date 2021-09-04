# CVTS

Misc stuff related to the CVTS project.

More complete documentation available [here](https://cvts.github.io/cvts/).



## Contents

- **bin**: Python scripts used in this project. These are documented in the the
  package documentation.

- **cvts**: Python code used in this project, structured as a Python package.

- **doc**: Sphinx documentation. Make this with `make sphinx-doc` (requires
  that you have run `make initial-setup` some time previously) and then access
  it at *doc/build/index.html*

- **Makefile**: Some common tasks.

- **notebooks**: Jupyter notebooks.

- **ops**: (Ansible) code for provisioning the system.

- **requirements.txt**: Python requirements.

- **[scripts](scripts/README.md)**: Convenience scripts mostly useful for dev.

- **setup.py**: Setup script for the python package.

- **test**: Example data for testing map matching (used by *test.sh*). Other
  file are written to this directory when *test.sh* is run.

    - **test.csv**: A test 'track' (can be prepared with *scripts/csv2json*).

- **test.sh**: A test script that downloads and prepares the data for Vietnam
  and runs an example CSV file against the
  [trace_attributes](https://valhalla.readthedocs.io/en/latest/api/map-matching/api-reference/#outputs-of-trace_attributes)
  service in 'one shot' mode. **Must be run in this folder.**

- **[windows](./windows/README.md)**: Stuff for setting up on windows...
  probably way out of date.



## Getting started

```bash
# Clone this repository
git clone git@github.com:cvts/cvts.git && cd cvts

# setup Valhalla
./scripts/setup-valhalla.sh

# make a virtual env
# Note that this installs for dev
make venv

# get the Vietnam data, set it up, and check that it is all working
./test.sh

# You deactivate the virtual env with
deactivate
```


Alternatively, for development in particular, you might say

```bash
make initial-setup
. venv/bin/activate
./test.sh
deactivate
```



## Config

Configuration is controlled by *cvts/settings.py*. This expects the environment
variable *CVTS_WORK_PATH* to be set, which specifies the root folder for
input/output data. One can optionally set specify the the following environment
variables which are read within *cvts/settings.py*.

### Environment Variables

#### General

- *CVTS_DEBUG*: Run in debug. `False` can be represented by *0* or *False*
  (anything else will be treated as `True`.


#### Data

- *CVTS_POSTGRES_CONNECTION_STRING*: A connection string for the Postgres DB to
  write outputs to. The string would look something like:

  *postgresql://\<username\>:\<password\>@\<host-ip-or-name\>:\<port\>/cvts*.

  I set this in my *~/.bashrc* as described below.

- *CVTS_RAW_DATA_FORMAT*: The 'format' the raw data is stored in. It does not
  actually reflect the raw format, but environments in which we have stored raw
  data previously. If this is set to *GZIP* then we are expecting a data layout
  implied by the script *cvts/_data_retrieval.py* (in this case the environment
  variables *DATALAKE_RAW_PATH* and *DATALAKE_CONNECTION_STRING* --- see
  below--- must be set also). Otherwise we are expecting
  a layout with:

    - a root folder containing a directories with names of the form *%Y%m%d*,
      where *%Y* is four digit year, *%m* is two digit month, and *%d* is two
      digit day.

    - CSV files for each day in these subfolders. The name of the file is
      interpreted as the vehicles identifier, the expected format is:

        ```
        Index,PlateNumber,Latitude,Longitude,speed,Orientation,VehicleType,Weight,Time
        1,1,108.189498901367,11.0894994735718,17,32,1,1,1501545628
        2,1,108.189796447754,11.0899000167847,9,302.5,1,1,1501545658
        3,1,108.189796447754,11.0899295806885,0,95.5,1,1,1501545779
        ```

- *CVTS_RAW_PATH*: The directory in which the raw data is stored.

- *CVTS_WORK_PATH*: The working directory. Defaults to *~/.cvts*. All other
  output directories (with the exception of the raw data directory) are
  created or assumed to exist under this directory if not otherwise specified.

- *CVTS_BOUNDARIES_PATH*: The directory in regional shape files are stored. If
  not specified it will be assumed to be under under the directory specified by
  *CVTS_WORK_PATH*. If that is not present and boundaries are required,
  something will go bang. I set this in my *.bashrc*.

- *CVTS_CONFIG_PATH*: The directory in which the configuration data is stored
  If that directory is not present and boundaries are required, something will
  go bang. If not specified, this will be assumed to exist under the directory
  specified by *CVTS_WORK_PATH*.

- *CVTS_OUTPUT_PATH*: The directory where outputs will be saved. If not
  specified, this will be created under the directory specified by
  *CVTS_WORK_PATH*.

- *DATALAKE_RAW_PATH*: The root folder for the 'data lake'. see
  *cvts/_data_retrieval.py* for how this is used.

- *DATALAKE_CONNECTION_STRING*: The connection string for the DB containing data
  about the 'data lake'. see *cvts/_data_retrieval.py* for how this is used.


#### PostgreSQL

Most results are saved in PostgreSQL.

I set the connection string up in my *~/.bashrc* with the following.

```bash
CVTS_POSTGRES_IP=localhost
export CVTS_POSTGRES_PORT=5432
export CVTS_POSTGRES_DB=cvts
export CVTS_POSTGRES_USER=cvts
export CVTS_POSTGRES_PASS=secure-password
export CVTS_POSTGRES_CONNECTION_STRING=postgresql://"$CVTS_POSTGRES_USER":"$CVTS_POSTGRES_PASS"@"$CVTS_POSTGRES_IP":"$CVTS_POSTGRES_PORT"/"$CVTS_POSTGRES_DB"
```

With these environment variables exported, the script
*scripts/start-docker-postgres.sh* is a convenient way of creating a local db
for testing.

To initially setup the DB... `sudo -u postgres psql`, then, at the prompt:

```bash
create database "$CVTS_POSTGRES_DB";
create user "$CVTS_POSTGRES_USER" with encrypted password "$CVTS_POSTGRES_PASS";
grant all privileges on database "$CVTS_POSTGRES_DB" to "$CVTS_POSTGRES_USER";
```

Something very similar to this is available in the make target *setup-postgre*.
It will use the username, password, PostgreSQL DB set in the environment
variables *CVTS_POSTGRES_USER*, *CVTS_POSTGRES_PASS* and *CVTS_POSTGRES_DB*.

To reinstall postgres completely, (see
[this](https://askubuntu.com/questions/817868/how-do-i-reinstall-postgresql-9-5-on-ubuntu-xenial-16-04-1)):

```bash
sudo apt-get --purge remove postgresql-*
sudo rm -Rf /etc/postgresql /var/lib/postgresql
sudo apt-get install postgresql
```

We use [sqlalchemy](https://www.sqlalchemy.org/) to define the DB and to access
the DB. The models are defined in *cvts/models.py*.
