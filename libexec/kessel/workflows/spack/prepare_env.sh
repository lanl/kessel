if [ -z "$KESSEL_PROJECT_SPEC" ]; then
  echo "ERROR: Invalid state '$KESSEL_PROJECT_SPEC' " >&2
  return 1
fi

if ! spack env activate --without-view "$KESSEL_ENVIRONMENT"; then
  spack env create --without-view "$KESSEL_ENVIRONMENT"
  spack env activate --without-view "$KESSEL_ENVIRONMENT"
  spack add "$KESSEL_PROJECT_SPEC"
fi

existing_lockfile="$SPACK_ENV/spack.lock.$(spack arch)"

if  [ ! -f "$SPACK_ENV/spack.lock" ] && [ -f "$existing_lockfile" ]; then
  cp "$existing_lockfile" "$SPACK_ENV/spack.lock"
  echo "Reusing existing lockfile for $(spack arch)"
  spack env activate --without-view "$KESSEL_ENVIRONMENT"
fi

# always disable view for now, until we know there is a use case that we need it
spack config add view:false

export KESSEL_PROJECT_NAME=$(spack-python -c "spec = spack.spec.Spec('$KESSEL_PROJECT_SPEC');print(spec.name)")

if [ -d "$KESSEL_SOURCE_DIR/spack_repo/$KESSEL_PROJECT_NAME" ]; then
  spack repo remove "$KESSEL_PROJECT_NAME" 2> /dev/null > /dev/null || true
  spack repo add "$KESSEL_SOURCE_DIR/spack_repo/$KESSEL_PROJECT_NAME"
fi

spack develop -b "$KESSEL_BUILD_DIR" -p "$KESSEL_SOURCE_DIR" --no-clone "$KESSEL_PROJECT_NAME"
spack config add "packages:${KESSEL_PROJECT_NAME}:package_attributes:keep_werror:all"

if [ -n "$KESSEL_GIT_MIRRORS" ]; then
  printf "%s\n" "$KESSEL_GIT_MIRRORS" | while IFS= read -r p
  do
    REPO_PATH=$(git -C $KESSEL_SOURCE_DIR/$p rev-parse --absolute-git-dir)
    EXT_NAME=$(basename "$p")
    echo "Creating Git Mirror for '${EXT_NAME}' pointing to file://${REPO_PATH}..."
    spack config add "packages:${EXT_NAME}:package_attributes:git:'file://${REPO_PATH}'"
  done
fi

if [ -n "${KESSEL_USER_BUILD_CACHE}" ]; then
  mkdir -p "${KESSEL_USER_BUILD_CACHE}"
  spack mirror add --type binary --autopush --unsigned user-ci-mirror "${KESSEL_USER_BUILD_CACHE}"
  spack buildcache update-index "${KESSEL_USER_BUILD_CACHE}" || true
fi
