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

if [ -z "$KESSEL_PROJECT_SPEC" ]; then
  echo "ERROR: Invalid state '$KESSEL_PROJECT_SPEC' " >&2
  return 1
fi

umask 0007

echo "Using Spack installation at $SPACK_ROOT"

extra_args=""

if ! $KESSEL_ENABLE_VIEW; then
  extra_args="--without-view"
fi

if ! spack env activate $extra_args "$KESSEL_SPACK_ENV"; then
  spack env create $extra_args "$KESSEL_SPACK_ENV"
  spack env activate $extra_args "$KESSEL_SPACK_ENV"
fi

existing_lockfile="$SPACK_ENV/spack.lock.$(spack arch)"

if  [ ! -f "$SPACK_ENV/spack.lock" ] && [ -f "$existing_lockfile" ]; then
  cp "$existing_lockfile" "$SPACK_ENV/spack.lock"
  echo "Reusing existing lockfile for $(spack arch)"
  spack env activate $extra_args "$KESSEL_SPACK_ENV"
fi

unset extra_args

if ! $KESSEL_ENABLE_VIEW; then
  spack config add view:false
fi

# chicken and egg problem: we need to figure out the project name before we can ask Spack
export KESSEL_PROJECT_NAME=$(echo "$KESSEL_PROJECT_SPEC" | awk '{print $1}' | sed 's/[@+~^%-].*//')

if [ -d "$KESSEL_SOURCE_DIR/spack_repo/$KESSEL_PROJECT_NAME" ]; then
  spack repo remove "$KESSEL_PROJECT_NAME" 2> /dev/null > /dev/null || true
  spack repo add "$KESSEL_SOURCE_DIR/spack_repo/$KESSEL_PROJECT_NAME"
fi

if spack find -r 2>/dev/null | grep -q "No root specs"; then
  spack add "$KESSEL_PROJECT_SPEC"
fi

# now that Spack "should" know about it, we'll ask again (TODO: is this still necessary?)
export KESSEL_PROJECT_NAME=$(spack-python -c "spec = spack.spec.Spec('$KESSEL_PROJECT_SPEC');print(spec.name)")

spack develop -b "$KESSEL_BUILD_DIR" -p "$KESSEL_SOURCE_DIR" --no-clone "$KESSEL_PROJECT_NAME"
spack config add "packages:${KESSEL_PROJECT_NAME}:package_attributes:keep_werror:all"


if [ -n "${KESSEL_USER_BUILD_CACHE}" ]; then
  mkdir -p "${KESSEL_USER_BUILD_CACHE}"
  spack mirror add --type binary --autopush --unsigned user-ci-mirror "${KESSEL_USER_BUILD_CACHE}"
  spack buildcache update-index "${KESSEL_USER_BUILD_CACHE}" || true
fi
