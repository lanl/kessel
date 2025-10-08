SCRIPT_PATH=${BASH_SOURCE[0]:-${(%):-%x}}
PARENT_DIR="$( cd "$( dirname "${SCRIPT_PATH}" )" &>/dev/null && pwd )"
export KESSEL_INIT="source $SCRIPT_PATH $@"

PROJECT_NAME=YOUR_PROJECT
export PROJECT_NAME_CHECKOUT=$(realpath $PARENT_DIR/..)
SYSTEM_NAME="local"
DEPLOYMENT_VERSION="2025-10-08"

if [ $# -ge 1 ]; then
  SYSTEM_NAME="$1"
  shift
fi

if [ ! -d "${KESSEL_ROOT}" ]; then
  if [[ "$SYSTEM_NAME" == "local" ]]; then
    echo "ERROR: Kessel must already be available on 'local' system." >&2
    false
    return
  elif [[ "$SYSTEM_NAME" == "darwin" || "$SYSTEM_NAME" == "rocinante" || "$SYSTEM_NAME" == "venado" || "${SYSTEM_NAME}" == "chicoma" ]]; then
    KESSEL_DEPLOYMENT=${KESSEL_DEPLOYMENT:-/usr/projects/$PROJECT_NAME/shared/spack-env/${DEPLOYMENT_VERSION}}
  elif [[ "$SYSTEM_NAME" == "rzadams" || "${SYSTEM_NAME}" == "rzansel" || "$SYSTEM_NAME" == "rzvernal" || "$SYSTEM_NAME" == "elcapitan" ]]; then
    KESSEL_DEPLOYMENT=${KESSEL_DEPLOYMENT:-/usr/workspace/$PROJECT_NAME/shared/spack-env/${DEPLOYMENT_VERSION}}
  else
    echo "ERROR: Unkown system '${SYSTEM_NAME}'" >&2
    false
    return
  fi

  KESSEL_ROOT="${KESSEL_DEPLOYMENT}/kessel"
fi

echo "Using Kessel installation at: ${KESSEL_ROOT}"
source "${KESSEL_ROOT}/share/kessel/setup-env.sh"

if [ -d "${KESSEL_DEPLOYMENT}" ]; then
  kessel deploy activate ${KESSEL_DEPLOYMENT}
fi
