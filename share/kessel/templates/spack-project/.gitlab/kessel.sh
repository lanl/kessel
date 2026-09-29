# Pick the KESSEL_DEPLOYMENT for this cluster, then source the shared helpers
# that ship inside the deployment's kessel.
# Intended to work on sh, zsh, and bash.
DEPLOYMENT_VERSION="2025-10-21"
SCRIPT_PATH=${BASH_SOURCE[0]:-${(%):-%x}}
PARENT_DIR="$( cd "$( dirname "${SCRIPT_PATH}" )" &>/dev/null && pwd )"

export PROJECT_CHECKOUT=$(realpath $PARENT_DIR/..)

# Just enough detection to choose the deployment path; kessel_detect_system does
# the rest.
if command -v jq >/dev/null 2>&1 && command -v sacctmgr >/dev/null 2>&1; then
  KESSEL_SYSTEM=$(sacctmgr list --json clusters | jq -r '.clusters[0].name')
elif command -v flux >/dev/null 2>&1; then
  KESSEL_SYSTEM=$(hostname | sed 's/[0-9]//g')
fi

if [ "$KESSEL_SYSTEM" = "darwin" ]; then
  export KESSEL_DEPLOYMENT=${KESSEL_DEPLOYMENT:-/usr/projects/YOUR_PROJECT/deployments/${DEPLOYMENT_VERSION}}
else
  echo "ERROR: Unknown system!" >&2
  return 1
fi

# Source the shared helpers (kessel_detect_system, kessel_activate_deployment).
_KESSEL_DEPLOYMENT_USE="$KESSEL_DEPLOYMENT/kessel/lib/kessel/workflows/base/spack/deployment/use.sh"
if [ ! -r "$_KESSEL_DEPLOYMENT_USE" ]; then
  echo "ERROR: $_KESSEL_DEPLOYMENT_USE not found (deployment missing or too old)!" >&2
  return 1
fi
source "$_KESSEL_DEPLOYMENT_USE"
unset _KESSEL_DEPLOYMENT_USE

kessel_parse_persist "$@" || return $?
kessel_detect_system
kessel_activate_deployment
