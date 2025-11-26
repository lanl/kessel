################################################################################
# Spack Deployment: Setup
################################################################################
source ${KESSEL_ROOT}/libexec/kessel/workflows/spack_deployment/common.sh

umask 0007
mkdir -p ${KESSEL_DEPLOYMENT}
chgrp ${KESSEL_GROUP} ${KESSEL_DEPLOYMENT} || true
chmod g+s ${KESSEL_DEPLOYMENT} || true

################################################################################
# clone Kessel into deployment
################################################################################
# keep track of originl kessel checkout that initiated the workflow
export KESSEL_INITIAL_ROOT="${KESSEL_INITIAL_ROOT:-${KESSEL_ROOT}}"

rm -rf "${KESSEL_DEPLOYMENT}/kessel"
git clone "$KESSEL_INITIAL_ROOT/.git" ${KESSEL_DEPLOYMENT}/kessel
source ${KESSEL_DEPLOYMENT}/kessel/share/kessel/setup-env.sh

################################################################################
# clone Spack into deployment
################################################################################
SPACK_CHECKOUT="${KESSEL_DEPLOYMENT}/spack"

if [ ! -d "${SPACK_CHECKOUT}" ]; then
  git clone -c feature.manyFiles=true --depth=1 "${SPACK_CHECKOUT_URL}" ${SPACK_CHECKOUT}
else
  git -C "${SPACK_CHECKOUT}" remote set-url origin "${SPACK_CHECKOUT_URL}"
fi

SPACK_HEAD=$(git -C "${SPACK_CHECKOUT}" rev-parse HEAD)

if [ "${SPACK_HEAD}" != "${SPACK_CHECKOUT_REF}" ]; then
  git -C "${SPACK_CHECKOUT}" fetch --depth=1 origin "${SPACK_CHECKOUT_REF}"
  git -C "${SPACK_CHECKOUT}" checkout FETCH_HEAD
  git -C "${SPACK_CHECKOUT}" branch -q -D "@{-1}"
fi

################################################################################
# write deployment configuration and environments
################################################################################

rm -rf "$KESSEL_DEPLOYMENT/config"
rm -rf "$KESSEL_DEPLOYMENT/environments"

copy_configuration
generate_environments

# link replicate tool
rm -rf "${KESSEL_DEPLOYMENT}/bin"
mkdir -p "${KESSEL_DEPLOYMENT}/bin"
ln -s ${KESSEL_ROOT}/libexec/kessel/workflows/spack_deployment/replicate_from_sqfs ${KESSEL_DEPLOYMENT}/bin/replicate

# generate activate.sh script for deployment
cp ${KESSEL_ROOT}/libexec/kessel/workflows/spack_deployment/activate.sh.in ${KESSEL_DEPLOYMENT}/activate.sh
sed -i 's/@KESSEL_PARENT_DEPLOYMENT@/\$KESSEL_DEPLOYMENT/g' ${KESSEL_DEPLOYMENT}/activate.sh
sed -i "s/@KESSEL_SYSTEM@/$KESSEL_SYSTEM/g" ${KESSEL_DEPLOYMENT}/activate.sh

# write kessel version used to generate this deployment
kessel --version > ${KESSEL_DEPLOYMENT}/.kessel_version

################################################################################
# activate deployment and setup git clones
################################################################################
kessel deploy activate "$KESSEL_DEPLOYMENT"

# clone spack/spack-packages
spack repo update builtin

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
