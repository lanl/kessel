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

PARENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" &>/dev/null && pwd)"
export KESSEL_SETUP_SCRIPT=$(realpath "${BASH_SOURCE[0]:-$0}")
export KESSEL_ROOT="$(realpath $PARENT_DIR/../..)"
export KESSEL_PARENT_PROMPT="$PS1"
unset IN_FISH

KESSEL_COLOR_BLUE='\033[1;34m'
KESSEL_COLOR_MAGENTA='\033[1;35m'
KESSEL_COLOR_CYAN='\033[1;36m'
KESSEL_COLOR_PLAIN='\033[0m'

PREFERRED_PYTHONS="python3.13 python3.12 python3.11 python3.8 python3 python"
PREFERRED_PYTHONS=($(echo "$PREFERRED_PYTHONS"))
for cmd in "${PREFERRED_PYTHONS[@]}"; do
    if command -v > /dev/null "$cmd"; then
        export KESSEL_PYTHON="$(command -v "$cmd")"
        break
    fi
done

_kessel_path_prepend() {
    if [ -d "$1" ] && [[ ":$PATH:" != *":$1:"* ]]; then
        PATH="$1${PATH:+":${PATH}"}"
    fi
}

kessel() {
    eval "$(command kessel "$@" 3>&1 >&4 4>&- || echo _kessel_ret=$?)" 4>&-
    return $_kessel_ret
} 4>&1

_kessel_path_prepend "${KESSEL_ROOT:+"${KESSEL_ROOT}/bin"}"

# Set up autocomplete
source $KESSEL_ROOT/share/kessel/kessel-completion.sh
