if [ -z "${ENVIRONMENTS}" ]; then
    export ENVIRONMENTS="$(spack env list | tr -d ' ')"
fi

install_options="--include-build-deps"
buildcache_options="--with-build-dependencies"
if [ "${KESSEL_BUILD_ROOTS}" != "true" ]; then
  install_options="--only dependencies $install_options"
  buildcache_options="--only dependencies $buildcache_options"
fi

status=0

printf "%s\n" "$ENVIRONMENTS" | while IFS= read -r ENVIRONMENT
do
  if [ -n "${ENVIRONMENT}" ]; then
    echo "Building '${ENVIRONMENT}' environment"
    spack env activate ${ENV_DIR:+${ENV_DIR}/}${ENVIRONMENT}

    if [ "${KESSEL_ENV_VIEWS}" != "true" ]; then
      spack config add view:false
    fi

    spack concretize -f --fresh

    # keep lock file for this architecture
    cp "$SPACK_ENV/spack.lock" "$SPACK_ENV/spack.lock.$(spack arch)"

    spack install $install_options

    if [ $? -ne 0 ]; then
      status=1
    fi

    if [ -n "$KESSEL_BUILD_CACHE_MIRROR" ]; then
      spack buildcache push $buildcache_options "${KESSEL_BUILD_CACHE_MIRROR}"
    fi
  fi
done

test $status -eq 0
