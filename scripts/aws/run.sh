#!/bin/bash
set -e
SCRIPT_DIR=$(dirname $0)
pushd $SCRIPT_DIR
if [ ! -d "env" ]
then
    echo "Installing requirements"
    virtualenv --quiet -p python3 env
    . env/bin/activate
    pip3 install --quiet -r infra/requirements.txt
fi
. env/bin/activate
python3 -m infra $@
popd
