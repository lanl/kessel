PARENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]:-$0}" )" &>/dev/null && pwd )"
export KESSEL_ROOT="$(realpath $PARENT_DIR/../..)"
export KESSEL_CONFIG_DIR="${KESSEL_ROOT}/etc/kessel"

_kessel_path_prepend() {
  if [ -d "$1" ] && [[ ":$PATH:" != *":$1:"* ]]; then
    PATH="$1${PATH:+":${PATH}"}"
  fi
}

_kessel_shell_wrapper() {
  _ks_subcommand=""
  case $_ks_subcommand in
    *)
      command kessel $@
      ;;
  esac
}

kessel() {
  _kessel_shell_wrapper $@
}

_kessel_path_prepend "${KESSEL_ROOT:+"${KESSEL_ROOT}/bin"}"
