#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

declare -a FILES_TO_TEST=("psll" "ascii_trees")

rm -f .coverage # Clear any previous .coverage report files

for NAME in "${FILES_TO_TEST[@]}"
do
    echo ""
    echo "Testing $NAME.py"
    coverage run -a --include="$NAME.py" -m unittest discover -p "test_$NAME.py" tests -v
    
    # Exit if unittests of this file failed
    if [ "$?" != "0" ]; then
        echo -e "${RED}Something is wrong${NC}"
        exit 1
    fi
done

echo ""
coverage report

# If -html option is passed, display the coverage report and delete the .coverage file
if [[ "$1" == "-html" ]]; then
    coverage html
    rm .coverage
    open ./htmlcov/index.html
else
    # Don't generate the html report on travis
    :
fi