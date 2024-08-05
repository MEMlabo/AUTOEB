#!/bin/bash

readonly EXEC_DIR=$(pwd)
readonly SHELL_DIR=$(dirname $0)

cd $SHELL_DIR
cd ../src/

# enter venv
. .venv/bin/activate

# execute AUTOEB
cd $EXEC_DIR
python3 -m autoeb $@
# exit venv
deactivate
