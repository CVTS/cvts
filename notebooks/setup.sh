#!/usr/bin/env bash

set -eu

main() {
    python3 -m virtualenv venv-notebooks
    . venv-notebooks/bin/activate
    python -m pip install -r requirements.txt
}

main "$@"
