# © 2026. Triad National Security, LLC. All rights reserved.
# This program was produced under U.S. Government contract 89233218CNA000001
# for Los Alamos National Laboratory (LANL), which is operated by Triad
# National Security, LLC for the U.S.  Department of Energy/National Nuclear
# Security Administration. All rights in the program are reserved by Triad
# National Security, LLC, and the U.S. Department of Energy/National Nuclear
# Security Administration. The Government is granted for itself and others
# acting on its behalf a nonexclusive, paid-up, irrevocable worldwide license
# in this material to reproduce, prepare derivative works, distribute copies to
# the public, perform publicly and display publicly, and to permit others to do
# so.
#
# Helpers for using an existing Spack deployment: detect the current system,
# activate the (possibly cloned) deployment, and allocate an interactive node.
# Intended to work on sh, zsh, and bash.

# Detect the current cluster (KESSEL_SYSTEM) and its scheduler
# (KESSEL_SYSTEM_SCHEDULER).
kessel_detect_system() {
  if command -v sacctmgr >/dev/null 2>&1 && command -v jq >/dev/null 2>&1; then
    KESSEL_SYSTEM=$(sacctmgr list --json clusters | jq -r '.clusters[0].name')
    KESSEL_SYSTEM_SCHEDULER="slurm"
  elif command -v flux >/dev/null 2>&1; then
    KESSEL_SYSTEM=$(hostname | sed 's/[0-9]//g')
    KESSEL_SYSTEM_SCHEDULER="flux"
  fi
  export KESSEL_SYSTEM KESSEL_SYSTEM_SCHEDULER
}

# Activate the writable workflow deployment (KESSEL_WORKFLOW_DEPLOYMENT),
# cloning it from the cluster deployment (KESSEL_DEPLOYMENT) if needed. Defaults
# to a per-user temp copy; set KESSEL_WORKFLOW_DEPLOYMENT to a path to persist it,
# or to "upstream" to use the (read-only) cluster deployment directly.
kessel_activate_deployment() {
  _KESSEL_WORKFLOW_DEPLOYMENT="$KESSEL_WORKFLOW_DEPLOYMENT"
  export KESSEL_WORKFLOW_DEPLOYMENT=${KESSEL_WORKFLOW_DEPLOYMENT:-${TMPDIR:-/tmp}/$USER-ci-envs}

  if [ "$KESSEL_WORKFLOW_DEPLOYMENT" = "upstream" ] && [ -d "$KESSEL_DEPLOYMENT" ]; then
    source "$KESSEL_DEPLOYMENT/activate.sh"
  else
    if [ -d "$KESSEL_DEPLOYMENT" ] && [ ! -d "$KESSEL_WORKFLOW_DEPLOYMENT" ]; then
      source "$KESSEL_DEPLOYMENT/activate.sh"
      echo "Creating writable deployment copy at $KESSEL_WORKFLOW_DEPLOYMENT"
      clone-deployment "$KESSEL_WORKFLOW_DEPLOYMENT" > /dev/null
    fi
    if [ ! -d "$KESSEL_WORKFLOW_DEPLOYMENT" ]; then
      echo "ERROR: $KESSEL_WORKFLOW_DEPLOYMENT does not exist!" >&2
      return 1
    elif [ -z "$_KESSEL_WORKFLOW_DEPLOYMENT" ] && [ ! -O "$KESSEL_WORKFLOW_DEPLOYMENT" ]; then
      echo "ERROR: $KESSEL_WORKFLOW_DEPLOYMENT not owned by $USER!" >&2
      return 1
    else
      source "$KESSEL_WORKFLOW_DEPLOYMENT/activate.sh"
    fi
  fi

  unset _KESSEL_WORKFLOW_DEPLOYMENT
}

# Allocate an interactive compute node and drop into the deployment on it. All
# arguments are forwarded to the scheduler as already-split allocation
# parameters. Requires kessel_detect_system to have set KESSEL_SYSTEM_SCHEDULER.
kessel_alloc() {
  _kessel_alloc_init="$KESSEL_DEPLOYMENT/kessel/lib/kessel/workflows/base/spack/deployment/alloc-init.sh"
  case "$KESSEL_SYSTEM_SCHEDULER" in
    slurm)
      echo "salloc $*" >&2
      export SHELL="$_kessel_alloc_init"
      salloc "$@"
      ;;
    flux)
      echo "flux alloc $* $_kessel_alloc_init" >&2
      flux alloc "$@" "$_kessel_alloc_init"
      ;;
    *)
      echo "ERROR: unknown scheduler '$KESSEL_SYSTEM_SCHEDULER'!" >&2
      unset _kessel_alloc_init
      return 1
      ;;
  esac
  unset _kessel_alloc_init
}
