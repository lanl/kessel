#KESSEL title: Configure
#KESSEL collapsed: true

if [ -z "$KESSEL_ENVIRONMENT" ] || [ -z "$KESSEL_ENVIRONMENT" ] || [ -z "$KESSEL_BUILD_DIR" ]; then
  echo "ERROR: Invalid state" >&2
  return 1
fi

export KESSEL_INSTALL_DIR="${KESSEL_INSTALL_DIR:-$KESSEL_BUILD_DIR/install}"

TEMP=()
while (( "$#" )); do
  case "$1" in
    -h|--help)
      usage
      return
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
      TEMP+=("$1")
      shift
      ;;
  esac
done

spack install --test root --include-build-deps -u cmake -v "$KESSEL_PROJECT_NAME"
export KESSEL_BUILD_ENV="$KESSEL_BUILD_DIR/build_env.sh"
$KESSEL_ROOT/libexec/kessel/workflows/spack/gen-build-env
(
source "$KESSEL_BUILD_ENV"
cmake -DCMAKE_VERBOSE_MAKEFILE=off -DCMAKE_INSTALL_PREFIX="$KESSEL_INSTALL_DIR" "$KESSEL_BUILD_DIR" 2> /dev/null > /dev/null
)
