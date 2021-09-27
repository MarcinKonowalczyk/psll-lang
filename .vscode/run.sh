# https://gist.github.com/MarcinKonowalczyk/709e93f08e9d72f8092acd5b8d34c81f
# Example .run.sh
echo "Hello from run script! ^_^"

# The direcotry of the main project from which this script is running
# https://stackoverflow.com/a/246128/2531987
ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
ROOT="${ROOT%/*}" # Strip .vscode folder
NAME="${ROOT##*/}" # Project name
PWD=$(pwd);

# Extension, filename and directory parts of the file which triggered this
# http://mywiki.wooledge.org/BashSheet#Parameter_Operations
FILE="$1"
FILENAME="${FILE##*/}" # Filename with extension
FILEPATH="${FILE%/*}" # Path of the current file
FILEFOLDER="${FILEPATH##*/}" # Folder in which the current file is located (could be e.g. a nested subdirectory)
EXTENSION="${FILENAME##*.}" # Just the extension
ROOTFOLDER="${1##*$ROOT/}" && ROOTFOLDER="${ROOTFOLDER%%/*}" # folder in the root directory (not necesarilly the same as FILEFOLDER)
[ $ROOTFOLDER != $FILENAME ] || ROOTFOLDER=""

# Echo of path variables
# VERBOSE=true
VERBOSE=false
if $VERBOSE; then
    # https://stackoverflow.com/a/5947802/2531987
    GREEN='\033[0;32m'; YELLOW='\033[0;33m'; RED='\033[0;31m'; NC='\033[0m'
    echo -e "ROOT       : $GREEN${ROOT}$NC  # root directory of the project"
    echo -e "NAME       : $GREEN${NAME}$NC  # project name"
    echo -e "PWD        : $GREEN${PWD}$NC  # pwd"
    echo -e "FILE       : $GREEN${FILE}$NC # full file information"
    echo -e "FILENAME   : $GREEN${FILENAME}$NC  # current filename"
    echo -e "FILEPATH   : $GREEN${FILEPATH}$NC  # path of the current file"
    echo -e "FILEFOLDER : $GREEN${FILEFOLDER}$NC  # folder in which the current file is located"
    echo -e "EXTENSION  : $GREEN${EXTENSION}$NC  # just the extension of the current file"
    if [ $ROOTFOLDER ]; then
        if [ $ROOTFOLDER != $FILEFOLDER ]; then
            echo -e "ROOTFOLDER : $GREEN${ROOTFOLDER}$NC # folder in the root directory"
        else
            echo -e "ROOTFOLDER : ${YELLOW}<same as FILEFOLDER>${NC}"
        fi
    else
        echo -e "ROOTFOLDER : ${YELLOW}<file in ROOT>${NC}"
    fi
fi

##################################################

bundle exec jekyll serve