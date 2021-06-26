#!/usr/bin/env bash
set -eu

main() {
    ansible-playbook -i inventory playbook.yaml
}

main "$@"
