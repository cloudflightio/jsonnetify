#!/bin/bash

set -eo pipefail

if [ -n "$1" ]; then
    curl "$1" -L --output manifest.yaml
    kubectl-slice -f manifest.yaml -o ./
    rm manifest.yaml
    for i in *.yaml; do yaml2jsonnet -o "$(basename "$i" .yaml).jsonnet" "$i"; done
    ls -l
    jsonnet -e -- "$(find . -name '*.jsonnet' -print0 | xargs -0 -I{} basename {} .jsonnet | sed -e '1i{' -e 's/.*/    "&": import "&.jsonnet",/' -e '$a}')" > manifest.libsonnet
    wc < manifest.libsonnet
else
    exec /bin/bash
fi