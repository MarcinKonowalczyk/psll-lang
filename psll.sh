#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Directories
DIR=`dirname $0` # This script's directory
PYRA="$DIR/Pyramid-Scheme/pyra.rb"

# Compile psll into pyramid scheme
PSLL_FILE="$PWD/${1%.*}.psll"
PYRA_FILE="$PWD/${1%.*}.pyra"

echo "Compiling psll to pyramid scheme"
python -m psll $PSLL_FILE -o $PYRA_FILE -f --full-names #-go #-co #-v
RESULT=$?

if [ "$RESULT" -ne 0 ]; then
    echo -e "${RED} > Compilation failed${NC}"
    exit $?
else
    echo -e "${GREEN} > Compilation successful${NC}"
fi

# Count characters in the file
wc $PSLL_FILE | awk {'print " > Psll file: " $2 " lines, " $3 " characters"'}
wc $PYRA_FILE | awk {'print " > Pyra file: " $2 " lines, " $3 " characters"'}
# Why, oh why is this ^ so hard to do with sed regular expressions...?

# Run pyramid scheme if compilation worked
echo "Running the scheme"
ruby $PYRA $PYRA_FILE "${@:2}"


