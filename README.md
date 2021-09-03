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


#### Postgres

Some results are saved in postgres.

I set the connection string up in my *~/.bashrc* with the following.

```bash
CVTS_POSTGRES_IP=localhost
export CVTS_POSTGRES_PORT=5432
export CVTS_POSTGRES_DB=cvts
export CVTS_POSTGRES_USER=cvts
export CVTS_POSTGRES_PASS=secure-password
export CVTS_POSTGRES_CONNECTION_STRING=postgresql://"$CVTS_POSTGRES_USER":"$CVTS_POSTGRES_PASS"@"$CVTS_POSTGRES_IP":"$CVTS_POSTGRES_PORT"/"$CVTS_POSTGRES_DB"
```

With these environment variables exported, the script *scripts/start-docker-postgres.sh* is a convenient way of creating a local db for testing.

To initially setup the DB... `sudo -u postgres psql`, then, at the prompt:

```bash
create database "$CVTS_POSTGRES_DB";
create user "$CVTS_POSTGRES_USER" with encrypted password "$CVTS_POSTGRES_PASS";
grant all privileges on database "$CVTS_POSTGRES_DB" to "$CVTS_POSTGRES_USER";
```

To (completely reinstall postgres completely, (see
[this](https://askubuntu.com/questions/817868/how-do-i-reinstall-postgresql-9-5-on-ubuntu-xenial-16-04-1)):

```bash
sudo apt-get --purge remove postgresql-*
sudo rm -Rf /etc/postgresql /var/lib/postgresql
sudo apt-get install postgresql
```
