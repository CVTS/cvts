#!/usr/bin/env bash

set -eu

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
NOTEBOOK_DIR=$(realpath ${SCRIPT_DIR}/../notebooks)

main() {
    cd ${NOTEBOOK_DIR}
    ./setup_venv.sh
    . venv-notebooks/bin/activate
    python -m jupyter lab --no-browser --port=7799
}

main "$@"
