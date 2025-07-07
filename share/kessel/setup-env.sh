PARENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" &>/dev/null && pwd)"
export KESSEL_ROOT="$(realpath $PARENT_DIR/../..)"
export KESSEL_CONFIG_DIR="${KESSEL_ROOT}/etc/kessel"
unset IN_FISH

_kessel_path_prepend() {
    if [ -d "$1" ] && [[ ":$PATH:" != *":$1:"* ]]; then
        PATH="$1${PATH:+":${PATH}"}"
    fi
}

kessel() {
    eval "$(command kessel "$@" 3>&1 >&4 4>&-)" 4>&-
} 4>&1

_kessel_path_prepend "${KESSEL_ROOT:+"${KESSEL_ROOT}/bin"}"

# Set up autocomplete
source $KESSEL_ROOT/share/kessel/kessel-completion.sh
