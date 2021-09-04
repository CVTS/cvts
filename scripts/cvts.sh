function cvts_env() {
    # $1: name of output and DB
    # $2: Debug or not (True/False)
    # $3: DB user to use
    unset "${!CVTS_@}"
    export CVTS_WORK_PATH=/mnt/data/cvts
    export CVTS_RAW_DATA_FORMAT=GZIP
    export CVTS_BOUNDARIES_PATH=/mnt/data/cvts/boundaries
    export CVTS_POSTGRES_PORT=5432
    export CVTS_POSTGRES_PASS=dont_use_this_password
    export CVTS_POSTGRES_HOST=localhost

    export CVTS_DEBUG=$2
    export CVTS_OUTPUT_PATH="$CVTS_WORK_PATH"/output_"$1"
    export CVTS_POSTGRES_DB=cvts_"$1"
    export CVTS_POSTGRES_USER="$3"
    export CVTS_POSTGRES_CONNECTION_STRING=postgresql://"$CVTS_POSTGRES_USER":"$CVTS_POSTGRES_PASS"@"$CVTS_POSTGRES_HOST":"$CVTS_POSTGRES_PORT"/"$CVTS_POSTGRES_DB"
}

function cvts_prod () {
    cvts_env v1 False cvts
}

function cvts_test() {
    cvts_env 'test' True cvts_test
}

cvts_test
