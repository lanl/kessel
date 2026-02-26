if [ -z "$SPACK_ENV" ] || [ -z "$KESSEL_BUILD_DIR" ]; then
  echo "ERROR: Invalid state" >&2
  return 1
fi

spack install --test root --include-build-deps -u cmake -v "$KESSEL_PROJECT_NAME"
export KESSEL_BUILD_ENV="$KESSEL_BUILD_DIR/build_env.sh"
$KESSEL_ROOT/libexec/kessel/workflows/spack/gen-build-env "$KESSEL_BUILD_ENV" "$KESSEL_PROJECT_NAME"
(
source "$KESSEL_BUILD_ENV"
cmake -DCMAKE_VERBOSE_MAKEFILE=off -DCMAKE_INSTALL_PREFIX="$KESSEL_INSTALL_DIR" "$@" "$KESSEL_BUILD_DIR"
)
