PARENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" &>/dev/null && pwd)"
export KESSEL_SETUP_SCRIPT=$(realpath "${BASH_SOURCE[0]:-$0}")
export KESSEL_ROOT="$(realpath $PARENT_DIR/../..)"
export KESSEL_CONFIG_DIR="${KESSEL_ROOT}/etc/kessel"
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

kessel_ci_message() {
    if [ "$CI" ]; then
        project=$1
        system=$2
        init=$3
        workflow=$4
        shift 4

        echo -e "${KESSEL_COLOR_BLUE} "
        echo "######################################################################"
        echo " "
        echo "To recreate this CI run, follow these steps:"
        echo " "
    
        if [[ "$system" != "local" ]]; then
            echo "ssh $system"
        fi
    
        echo "cd /your/$project/checkout"
    
        if [[ "${LLNL_FLUX_SCHEDULER_PARAMETERS}" ]]; then
          echo "flux alloc ${LLNL_FLUX_SCHEDULER_PARAMETERS}"
        elif [[ "${SCHEDULER_PARAMETERS}" ]]; then
          echo "salloc ${SCHEDULER_PARAMETERS}"
        fi
    
        if [ "$init" ]; then
            echo "$init"
        fi
    
        if [ -n "$workflow" ] && [[ "$workflow" != "default" ]]; then
            echo "kessel workflow activate $workflow"
        fi
    
        echo "kessel run $@"
        echo " "
        echo "######################################################################"
        echo -e "${KESSEL_COLOR_PLAIN} "
    fi
}

kessel() {
    eval "$(command kessel "$@" 3>&1 >&4 4>&-)" 4>&-
} 4>&1

_kessel_path_prepend "${KESSEL_ROOT:+"${KESSEL_ROOT}/bin"}"

# Set up autocomplete
source $KESSEL_ROOT/share/kessel/kessel-completion.sh
