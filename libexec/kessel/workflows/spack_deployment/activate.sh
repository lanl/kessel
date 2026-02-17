echo "Activating deployment at ${KESSEL_DEPLOYMENT}"

export _OLD_PATH=$PATH

add_to_path() {
  dir=$1
  case ":$PATH:" in
    *":$dir:"*) ;;
    *) PATH="$dir:$PATH" ;;
  esac
}

deactivate() {
  kessel reset
  export PATH=$_OLD_PATH
  unset SPACK_DISABLE_LOCAL_CONFIG
  unset SPACK_USER_CACHE_PATH
  unset SPACK_SKIP_MODULES
  unset SPACK_USER_CONFIG_PATH
  unset SPACK_SYSTEM_CONFIG_PATH
  unset SPACK_ROOT
  unset KESSEL_ROOT
}

add_to_path "$KESSEL_DEPLOYMENT/bin"
export PATH

export KESSEL_CURRENT_SYSTEM="${KESSEL_CURRENT_SYSTEM:-${KESSEL_SYSTEM}}"

unset SPACK_DISABLE_LOCAL_CONFIG
export SPACK_USER_CACHE_PATH="$KESSEL_DEPLOYMENT/.spack"
export SPACK_SKIP_MODULES=true
export SPACK_USER_CONFIG_PATH="$KESSEL_DEPLOYMENT/.spack"
export SPACK_SYSTEM_CONFIG_PATH="$KESSEL_CONFIG_DIR"

source "$KESSEL_DEPLOYMENT/spack/share/spack/setup-env.sh"
