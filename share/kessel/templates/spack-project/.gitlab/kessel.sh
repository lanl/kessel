SCRIPT_PATH=${BASH_SOURCE[0]:-${(%):-%x}}
PARENT_DIR="$( cd "$( dirname "${SCRIPT_PATH}" )" &>/dev/null && pwd )"
export KESSEL_WORKFLOW_DEPLOYMENT="${KESSEL_WORKFLOW_DEPLOYMENT:-${TMPDIR:-/tmp}/$USER-ci-envs}"
export KESSEL_INIT="source $SCRIPT_PATH $@"

PROJECT_NAME=YOUR_PROJECT
export YOUR_PROJECT_CHECKOUT=$(realpath $PARENT_DIR/..)
SYSTEM_NAME="local"
DEPLOYMENT_VERSION="2025-10-08"

if [ $# -ge 1 ]; then
  SYSTEM_NAME="$1"
  shift
fi

if [ ! -d "${KESSEL_ROOT}" ]; then
  if [[ "$SYSTEM_NAME" == "local" ]]; then
    echo "ERROR: Kessel must already be available on 'local' system." >&2
    return 1
  elif [[ "$SYSTEM_NAME" == "darwin" || "$SYSTEM_NAME" == "rocinante" ]]; then
    KESSEL_DEPLOYMENT=${KESSEL_DEPLOYMENT:-/usr/projects/$PROJECT_NAME/shared/spack-env/${DEPLOYMENT_VERSION}}
  elif [[ "$SYSTEM_NAME" == "rzadams" || "$SYSTEM_NAME" == "rzvernal" || "$SYSTEM_NAME" == "elcapitan" || "$SYSTEM_NAME" == "tuolumne" ]]; then
    KESSEL_DEPLOYMENT=${KESSEL_DEPLOYMENT:-/usr/workspace/$PROJECT_NAME/shared/spack-env/${DEPLOYMENT_VERSION}}
  else
    echo "ERROR: Unkown system '${SYSTEM_NAME}'" >&2
    return 1
  fi

  KESSEL_ROOT="${KESSEL_DEPLOYMENT}/kessel"
fi

echo "Using Kessel installation at: ${KESSEL_ROOT}"
source "${KESSEL_ROOT}/share/kessel/setup-env.sh"

if [ -d "${KESSEL_DEPLOYMENT}" ]; then
  kessel deploy replicate ${KESSEL_DEPLOYMENT} ${KESSEL_WORKFLOW_DEPLOYMENT}
  kessel deploy activate ${KESSEL_WORKFLOW_DEPLOYMENT}
fi

kessel system activate ${SYSTEM_NAME}
