umask 0007
mkdir -p ${KESSEL_DEPLOYMENT}
chgrp ${KESSEL_GROUP} ${KESSEL_DEPLOYMENT} || true
chmod g+s ${KESSEL_DEPLOYMENT} || true

# keep track of originl kessel checkout that initiated the workflow
export KESSEL_INITIAL_ROOT="${KESSEL_INITIAL_ROOT:-${KESSEL_ROOT}}"

rm -rf "${KESSEL_DEPLOYMENT}/kessel"
git clone "$KESSEL_INITIAL_ROOT/.git" ${KESSEL_DEPLOYMENT}/kessel

source ${KESSEL_DEPLOYMENT}/kessel/share/kessel/setup-env.sh

(
    cd ${KESSEL_DEPLOYMENT}
    kessel deploy init ${KESSEL_DEPLOYMENT_CONFIG}
    rm -rf "${KESSEL_DEPLOYMENT}/.kessel"
    mkdir "${KESSEL_DEPLOYMENT}/.kessel"
    if [ -f "${KESSEL_DEPLOYMENT_CONFIG}/.kessel/replicate" ]; then
        cp "${KESSEL_DEPLOYMENT_CONFIG}/.kessel/replicate" "${KESSEL_DEPLOYMENT}/.kessel/"
    fi
)

kessel deploy activate "$KESSEL_DEPLOYMENT"
kessel system activate "$KESSEL_SYSTEM"

clone_and_sync() {
    src_checkout="$1"
    src=$(git -C "$1" rev-parse --absolute-git-dir)
    src_rev=$(git -C "$1" rev-parse HEAD)
    dest="$2"
    echo "$src -> $dest"
    $KESSEL_ROOT/libexec/kessel/tools/update_local_branches "$src_checkout"
    git -c advice.detachedhead=false -C "$src_checkout" checkout "$src_rev"
    git -C "$src_checkout" fetch --tags
    mkdir -p $(dirname "$dest")
    rm -rf "$dest"
    git -c advice.detachedhead=false clone "$src" "$dest"
    git -C "$dest" fetch --tags
    $KESSEL_ROOT/libexec/kessel/tools/update_local_branches "$dest"
    git -c advice.detachedhead=false -C "$dest" checkout "$src_rev"
}

if [ -n "$KESSEL_GIT_MIRRORS" ]; then
  printf "%s\n" "$KESSEL_GIT_MIRRORS" | while IFS= read -r p
  do
    if [ -n "$p" ]; then
      clone_and_sync "$KESSEL_DEPLOYMENT_CONFIG/$p" "$KESSEL_DEPLOYMENT/$p"
    fi
  done
fi

if [ -n "$KESSEL_BUILD_CACHE_MIRROR" ]; then
  mkdir -p "${KESSEL_BUILD_CACHE_MIRROR}"
fi
