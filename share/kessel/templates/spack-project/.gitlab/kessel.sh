DEPLOYMENT_VERSION="2025-10-21"
SCRIPT_PATH=${BASH_SOURCE[0]:-${(%):-%x}}
PARENT_DIR="$( cd "$( dirname "${SCRIPT_PATH}" )" &>/dev/null && pwd )"

export KESSEL_INIT="source $SCRIPT_PATH"
export FLECSI_CHECKOUT=$(realpath $PARENT_DIR/..)

if command -v jq >/dev/null 2>&1 && command -v sacctmgr >/dev/null 2>&1; then
  SYSTEM_NAME=$(sacctmgr list --json clusters  | jq -r '.clusters[0].name')
elif command -v flux >/dev/null 2>&1; then
  SYSTEM_NAME=$(hostname | sed 's/[0-9]//g')
fi

# During a regular CI run the workflow deployment is always a temporary copy of
# the cluster deployment to allow customization. This can be overwritten by
# setting KESSEL_WORKFLOW_DEPLOYMENT to another persistent location.
export KESSEL_WORKFLOW_DEPLOYMENT="${KESSEL_WORKFLOW_DEPLOYMENT:-${TMPDIR:-/tmp}/$USER-ci-envs}"

if [ "$SYSTEM_NAME" = "darwin" ]; then
  export KESSEL_DEPLOYMENT=${KESSEL_DEPLOYMENT:-/usr/projects/YOUR_PROJECT/deployments/${DEPLOYMENT_VERSION}}
else
  echo "ERROR: Unknown system!" >&2
  return 1
fi

KESSEL_ROOT="${KESSEL_DEPLOYMENT}/kessel"

if [ -d "$KESSEL_ROOT" ]; then
  echo "Using Kessel installation at: ${KESSEL_ROOT}"
  source "${KESSEL_ROOT}/share/kessel/setup-env.sh"
else
  echo "ERROR: Could not find kessel installation!" >&2
  return 1
fi

if [ -d "${KESSEL_DEPLOYMENT}" ] && [ ! -d "${KESSEL_WORKFLOW_DEPLOYMENT}" ]; then
  kessel deploy activate "${KESSEL_DEPLOYMENT}"
  kessel deploy replicate "${KESSEL_WORKFLOW_DEPLOYMENT}"
fi

kessel deploy activate "${KESSEL_WORKFLOW_DEPLOYMENT}"
kessel system activate "${SYSTEM_NAME}"
