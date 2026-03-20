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

if [ -z "${ENVIRONMENTS}" ]; then
    export ENVIRONMENTS="$(spack env list | tr -d ' ')"
fi

install_options="--include-build-deps"
buildcache_options="--unsigned --with-build-dependencies"
if [ "${KESSEL_BUILD_ROOTS}" != "true" ]; then
  install_options="--only dependencies $install_options"
  buildcache_options="--only dependencies $buildcache_options"
fi

rc=0

printf "%s\n" "$ENVIRONMENTS" | while IFS= read -r ENVIRONMENT
do
  if [ -n "${ENVIRONMENT}" ]; then
    echo "Building '${ENVIRONMENT}' environment"
    spack env activate ${ENV_DIR:+${ENV_DIR}/}${ENVIRONMENT} || rc=1

    if [ "${KESSEL_ENV_VIEWS}" != "true" ]; then
      spack config add view:false
    fi

    spack concretize -f --fresh || rc=1

    # keep lock file for this architecture
    cp "$SPACK_ENV/spack.lock" "$SPACK_ENV/spack.lock.$(spack arch)" || rc=1

    spack install $install_options || rc=1

    if [ -n "$KESSEL_BUILD_CACHE_MIRROR" ]; then
      spack buildcache push $buildcache_options "${KESSEL_BUILD_CACHE_MIRROR}"
    fi
  fi
done

return $rc
