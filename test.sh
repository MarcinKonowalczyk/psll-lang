#!/bin/bash

# Parse flags
while getopts "cehr" flag
do
    case "${flag}" in
        c) c=true;;
        e) e=true;;
        h) h=true;;
        r) r=true;c=true;; # Must run coverage to show the report
    esac
done

# Display help
if [[ "$h" == true ]]; then
    echo "Usage: ./test.sh [-h | -c | -r]"
    echo "Helper bash script for running tests"
    echo " -h  -  display help"
    echo " -c  -  run with coverage"
    echo " -e  -  also test examples"
    echo " -r  -  show html report. implies -c."
    exit 0
fi

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

declare -a FILES_TO_TEST=("psll" "ascii_trees")

[ $c ] && rm -f .coverage # Clear any previous .coverage report files

for NAME in "${FILES_TO_TEST[@]}"
do
    echo ""
    echo "Testing $NAME.py"
    if [ $c ]; then
        coverage run --append --include="$NAME.py" -m unittest discover -p "test_$NAME.py" tests -v;
    else
        python -m unittest discover -p "test_$NAME.py" tests -v;
    fi
    
    # Exit if unittests of this file failed
    if [ "$?" != "0" ]; then
        echo -e "${RED}Something is wrong${NC}"
        exit 1
    fi
done

[ $e ] && python -m unittest discover -p "test_examples.py" tests -v

[ $c ] && echo "" && coverage report

# If -r option is passed, display the coverage report and delete the .coverage file
if [ $r ]; then
    coverage html
    rm .coverage
    open ./htmlcov/index.html
fi