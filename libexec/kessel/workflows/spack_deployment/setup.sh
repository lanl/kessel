################################################################################
# Spack Deployment: Setup
################################################################################
source ${KESSEL_ROOT}/libexec/kessel/workflows/spack_deployment/common.sh

umask 0007
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
# clone default configurations into deployment
################################################################################
SITE_CONFIGS_CHECKOUT="${KESSEL_DEPLOYMENT}/config/site"

rm -rf "${KESSEL_DEPLOYMENT}/config"
mkdir -p "$KESSEL_DEPLOYMENT/config"

if [ ! -d "${SITE_CONFIGS_CHECKOUT}" ]; then
  git clone "${SITE_CONFIGS_CHECKOUT_URL}" ${SITE_CONFIGS_CHECKOUT}
else
  git -C "${SITE_CONFIGS_CHECKOUT}" remote set-url origin "${SITE_CONFIGS_CHECKOUT_URL}"
fi

SITE_CONFIGS_HEAD=$(git -C "${SITE_CONFIGS_CHECKOUT}" rev-parse HEAD)

if [ "${SITE_CONFIGS_HEAD}" != "${SITE_CONFIGS_CHECKOUT_REF}" ]; then
  git -C "${SITE_CONFIGS_CHECKOUT}" fetch origin "${SITE_CONFIGS_CHECKOUT_REF}"
  git -C "${SITE_CONFIGS_CHECKOUT}" checkout FETCH_HEAD
  git -C "${SITE_CONFIGS_CHECKOUT}" branch -q -D "@{-1}" || true
fi

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
  git -C "${SPACK_CHECKOUT}" branch -q -D "@{-1}" || true
fi

################################################################################
# write deployment configuration and environments
################################################################################

copy_configuration
generate_environments

# link clone tool
rm -rf "${KESSEL_DEPLOYMENT}/bin"
mkdir -p "${KESSEL_DEPLOYMENT}/bin"

if ${KESSEL_ALLOW_REPLICATE}; then
  ln -s ${KESSEL_ROOT}/libexec/kessel/workflows/spack_deployment/clone_from_sqfs ${KESSEL_DEPLOYMENT}/bin/clone-deployment
fi

# write kessel version used to generate this deployment
kessel --version > ${KESSEL_DEPLOYMENT}/.kessel_version

################################################################################
# activate deployment and setup git clones
################################################################################
source "${KESSEL_DEPLOYMENT}/activate.sh"

# clone spack/spack-packages
spack repo update builtin


if [ -n "$KESSEL_BUILD_CACHE_MIRROR" ]; then
  mkdir -p "${KESSEL_BUILD_CACHE_MIRROR}"
fi
