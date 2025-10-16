SCRIPT_PATH=${BASH_SOURCE[0]:-${(%):-%x}}
PARENT_DIR="$( cd "$( dirname "${SCRIPT_PATH}" )" &>/dev/null && pwd )"
export KESSEL_INIT="source $SCRIPT_PATH"
source $PARENT_DIR/../share/kessel/setup-env.sh
