# https://gist.github.com/MarcinKonowalczyk/709e93f08e9d72f8092acd5b8d34c81f
echo "hi! ^_^"

# Extension, filename and directory parts of the file which triggered this
EXTENSION="${1##*.}"
FILENAME=$(basename -- "$1")
DIR="${1%/*}/"

# The direcotry of the file folder from which this script is running
# https://stackoverflow.com/a/246128/2531987
ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
ROOT="${ROOT%/*}/"

# Debug print
echo "EXTENSION : ${EXTENSION}"
echo "FILENAME : ${FILENAME}"
echo "DIR : ${DIR}"
echo "ROOT : ${ROOT}"

PARENT_FOLDER=${DIR%/}
PARENT_FOLDER=${PARENT_FOLDER##*/}

# Run make from the sigbovik-paper directory
if [ "$PARENT_FOLDER" = "sigbovik-paper" ]; then
    make --directory "${DIR}";
elif [[ "$PARENT_FOLDER" = "examples" ]] && [[ "$EXTENSION" == "psll" ]]; then
# elif [ "$PARENT_FOLDER" = "examples" && "$EXTENSION" == "psll" ]; then
    ${ROOT}psll.sh examples/$FILENAME
else
    :
fi
# make;
# make clean && make pdf;