umask 0007

export KESSEL_ENVIRONMENT="${KESSEL_ENVIRONMENT:-default}"

export KESSEL_SOURCE_DIR="$PWD"
export KESSEL_BUILD_DIR="${PWD}/build"
export KESSEL_INSTALL_DIR="$KESSEL_BUILD_DIR/install"

FULL_ARGS="$@"

TEMP=""
while (( "$#" )); do
  case "$1" in
    -h|--help)
      usage
      return
      ;;
    -e|--env)
      if [ -n "$2" ] && [[ "$2" != -* ]]; then
         export KESSEL_ENVIRONMENT="$2"
         shift 2
      else
         echo "ERROR: -e/--env requires an argument." >&2
         return 1
      fi
      ;;
    --env=*)
      export KESSEL_ENVIRONMENT=${1#*=}
      shift
      ;;
    -S|--source-dir)
      if [ -n "$2" ] && [[ "$2" != -* ]]; then
         export KESSEL_SOURCE_DIR="$2"
         shift 2
      else
         echo "ERROR: -S/--source-dir requires an argument." >&2
         return 1
      fi
      ;;
    --source-dir=*)
      export KESSEL_INSTALL_DIR=${1#*=}
      shift
      ;;
    -B|--build-dir)
      if [ -n "$2" ] && [[ "$2" != -* ]]; then
         export KESSEL_BUILD_DIR="$2"
         shift 2
      else
         echo "ERROR: -B/--build-dir requires an argument." >&2
         return 1
      fi
      ;;
    --build-dir=*)
      export KESSEL_BUILD_DIR=${1#*=}
      shift
      ;;
    -I|--install-dir)
      if [ -n "$2" ] && [[ "$2" != -* ]]; then
         export KESSEL_INSTALL_DIR="$2"
         shift 2
      else
         echo "ERROR: -I/--install-dir requires an argument." >&2
         return 1
      fi
      ;;
    --install-dir=*)
      export KESSEL_INSTALL_DIR=${1#*=}
      shift
      ;;
    -*|--*)
      echo "ERROR: invalid option $1" >&2
      return 1
      ;;
    *)
      TEMP="$TEMP $1"
      shift
      ;;
  esac
done

if [ -n "$TEMP" ]; then
  export KESSEL_PROJECT_SPEC="$TEMP"
fi

if [[ ! -d "$KESSEL_DEPLOYMENT" ]]; then
  if [[ -z "$SPACK_ROOT" ]]; then
    echo "ERROR: No active Spack installation!" >&2
    return 1
  else
    echo "Using Spack install at $SPACK_ROOT"
  fi
fi

export KESSEL_PROJECT_NAME=$(spack-python -c "spec = spack.spec.Spec('$KESSEL_PROJECT_SPEC');print(spec.name)")
kessel_ci_message "$KESSEL_PROJECT_NAME" "$KESSEL_CURRENT_SYSTEM" "$KESSEL_INIT" "$KESSEL_WORKFLOW" "$FULL_ARGS"
