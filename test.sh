#!/bin/bash

# Parse flags
while getopts "cehr" flag; do
    case "${flag}" in
    c) c=true ;;
    e) e=true ;;
    h) h=true ;;
    r)
        r=true
        c=true
        ;; # Must run coverage to show the report
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

COVERAGE="$(command -v coverage)"
if [ -z "$COVERAGE" ]; then
    COVERAGE="uv run coverage"
fi

if [ $c ]; then
    echo "Running tests with coverage"
    echo "---------------------------"
    # Collect coverage for each file individually to not artificially increase coverage
    declare -a FILES_TO_COVER=("ascii_trees" "lexer" "macros" "optimisers" "preprocessor")
    ${COVERAGE} erase
    for NAME in "${FILES_TO_COVER[@]}"; do
        echo -e "${GREEN}Collecting coverage for $NAME.py${NC}"
        ${COVERAGE} run --append --include="./psll/$NAME.py" -m pytest -k "not examples" --no-subtests-shortletter --quiet

        # Exit if unittests of this file failed
        if [ "$?" != "0" ]; then
            echo -e "${RED}Something is wrong${NC}"
            exit 1
        fi
    done
else
    echo "Running tests without coverage"
    echo "------------------------------"
    pytest -k "not examples"
fi

[ $e ] && pytest -k "examples" --quiet

[ $c ] && echo "" && coverage report

# If -r option is passed, display the coverage report and delete the .coverage file
if [ $r ]; then
    coverage html
    rm .coverage
    open ./htmlcov/index.html
fi
