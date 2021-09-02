#!/usr/bin/env bash

set -eu


main() {

    cd notebooks
    . venv-notebooks/bin/activate
    python -m jupyter lab --no-browser --port=7799
}

main "$@"
