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

if [ -z "$SPACK_ENV" ] || [ -z "$KESSEL_BUILD_DIR" ]; then
  echo "ERROR: Invalid state" >&2
  return 1
fi

spack install --test root --include-build-deps -u cmake -v "$KESSEL_PROJECT_NAME"
export KESSEL_BUILD_ENV="$KESSEL_BUILD_DIR/build_env.sh"
$KESSEL_ROOT/lib/kessel/workflows/base/spack/build_environment/gen-build-env "$KESSEL_BUILD_ENV" "$KESSEL_PROJECT_NAME"
(
source "$KESSEL_BUILD_ENV"
cmake -DCMAKE_VERBOSE_MAKEFILE=off -DCMAKE_INSTALL_PREFIX="$KESSEL_INSTALL_DIR" "$@" "$KESSEL_BUILD_DIR"
)
