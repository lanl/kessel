source ${KESSEL_ROOT}/libexec/kessel/workflows/spack_deployment/common.sh
export KESSEL_DEPLOYMENT_CONFIG=${KESSEL_DEPLOYMENT_CONFIG:-$PWD}

copy_configuration
generate_environments

if [ -n "$KESSEL_BUILD_CACHE_MIRROR" ]; then
  spack buildcache update-index "${KESSEL_BUILD_CACHE_MIRROR}"
fi

spack clean -sdfmp

echo "Setting permissions and group (excluding spack/opt/spack) ..."
find "$KESSEL_DEPLOYMENT" -path "$KESSEL_DEPLOYMENT/spack/opt/spack" -prune -o -exec chown -h ":$KESSEL_GROUP" {} +
find "$KESSEL_DEPLOYMENT" -path "$KESSEL_DEPLOYMENT/spack/opt/spack" -prune -o -type d -exec chmod "$KESSEL_PERMISSIONS" {} +
find "$KESSEL_DEPLOYMENT" -path "$KESSEL_DEPLOYMENT/spack/opt/spack" -prune -o -type f -exec chmod "$KESSEL_PERMISSIONS" {} +

find "$KESSEL_DEPLOYMENT/spack/opt/spack/bin" -exec chown -h ":$KESSEL_GROUP" {} +
find "$KESSEL_DEPLOYMENT/spack/opt/spack/bin" -type d -exec chmod "$KESSEL_PERMISSIONS" {} +
find "$KESSEL_DEPLOYMENT/spack/opt/spack/bin" -type f -exec chmod "$KESSEL_PERMISSIONS" {} +

find "$KESSEL_DEPLOYMENT/spack/opt/spack/.spack-db" -exec chown -h ":$KESSEL_GROUP" {} +
find "$KESSEL_DEPLOYMENT/spack/opt/spack/.spack-db" -type d -exec chmod "$KESSEL_PERMISSIONS" {} +
find "$KESSEL_DEPLOYMENT/spack/opt/spack/.spack-db" -type f -exec chmod "$KESSEL_PERMISSIONS" {} +

chmod g+s "$KESSEL_DEPLOYMENT/spack/opt/spack/.spack-db"

if ${KESSEL_ALLOW_REPLICATE}; then
  SQFS_FILE="$KESSEL_DEPLOYMENT/.replicate.sqfs"
  "$KESSEL_ROOT/libexec/kessel/workflows/spack_deployment/gen_replicate_sqfs" "$KESSEL_DEPLOYMENT" "$SQFS_FILE"
  chown ":$KESSEL_GROUP" "$SQFS_FILE"
  chmod "$KESSEL_PERMISSIONS" "$SQFS_FILE"
fi

echo "Setting permissions and group of spack/opt/spack ..."
chown -R ":$KESSEL_GROUP" "$KESSEL_DEPLOYMENT/spack/opt/spack"
chmod -R "$KESSEL_PERMISSIONS" "$KESSEL_DEPLOYMENT/spack/opt/spack"
chmod g+s "$KESSEL_DEPLOYMENT/spack/opt/spack/.spack-db"
