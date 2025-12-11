source ${KESSEL_ROOT}/libexec/kessel/workflows/spack_deployment/common.sh
export KESSEL_DEPLOYMENT_CONFIG=${KESSEL_DEPLOYMENT_CONFIG:-$PWD}

copy_configuration
generate_environments

if [ -n "$KESSEL_BUILD_CACHE_MIRROR" ]; then
  spack buildcache update-index "${KESSEL_BUILD_CACHE_MIRROR}"
fi

spack clean -a

echo "Setting permissions and group..."
chown -R ":$KESSEL_GROUP" "$KESSEL_DEPLOYMENT"
chmod -R "$KESSEL_PERMISSIONS" "$KESSEL_DEPLOYMENT"

chmod g+s "$KESSEL_DEPLOYMENT/spack/opt/spack/.spack-db"

SQFS_FILE="$KESSEL_DEPLOYMENT/.replicate.sqfs"
"$KESSEL_ROOT/libexec/kessel/workflows/spack_deployment/gen_replicate_sqfs" "$KESSEL_DEPLOYMENT" "$SQFS_FILE"
chown ":$KESSEL_GROUP" "$SQFS_FILE"
chmod "$KESSEL_PERMISSIONS" "$SQFS_FILE"
