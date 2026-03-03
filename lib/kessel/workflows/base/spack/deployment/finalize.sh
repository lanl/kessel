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

source ${KESSEL_ROOT}/lib/kessel/workflows/base/spack/deployment/common.sh
export KESSEL_DEPLOYMENT_CONFIG=${KESSEL_DEPLOYMENT_CONFIG:-$PWD}

copy_configuration
generate_environments

if [ -n "$KESSEL_BUILD_CACHE_MIRROR" ]; then
  spack buildcache update-index "${KESSEL_BUILD_CACHE_MIRROR}"
fi

spack clean -sdfmp

git -C $KESSEL_DEPLOYMENT/spack gc --aggressive --prune=now
git -C $KESSEL_DEPLOYMENT/spack-packages gc --aggressive --prune=now

echo "Setting permissions and group (excluding spack/opt/spack) ..."
find "$KESSEL_DEPLOYMENT" -path "$KESSEL_DEPLOYMENT/spack/opt/spack" -prune -o -exec chown -h ":$KESSEL_GROUP" {} +
find "$KESSEL_DEPLOYMENT" -path "$KESSEL_DEPLOYMENT/spack/opt/spack" -prune -o -type d -exec chmod "$KESSEL_PERMISSIONS" {} +
find "$KESSEL_DEPLOYMENT" -path "$KESSEL_DEPLOYMENT/spack/opt/spack" -prune -o -type f -exec chmod "$KESSEL_PERMISSIONS" {} +

find "$KESSEL_DEPLOYMENT/spack/opt/spack/bin" -exec chown -h ":$KESSEL_GROUP" {} +
find "$KESSEL_DEPLOYMENT/spack/opt/spack/bin" -type d -exec chmod "$KESSEL_PERMISSIONS" {} +
find "$KESSEL_DEPLOYMENT/spack/opt/spack/bin" -type f -exec chmod "$KESSEL_PERMISSIONS" {} +

# find .spack-db directory, since it is dependent on whether we're using prefix padding
_SPACK_DB_DIR=$(find $KESSEL_DEPLOYMENT/spack/opt/spack -type d -name .spack-db -print -quit)

if [ -d "$_SPACK_DB_DIR" ]; then
  find "$_SPACK_DB_DIR" -exec chown -h ":$KESSEL_GROUP" {} +
  find "$_SPACK_DB_DIR" -type d -exec chmod "$KESSEL_PERMISSIONS" {} +
  find "$_SPACK_DB_DIR" -type f -exec chmod "$KESSEL_PERMISSIONS" {} +

  chmod g+s "$_SPACK_DB_DIR"
fi

if ${KESSEL_ALLOW_REPLICATE}; then
  SQFS_FILE="$KESSEL_DEPLOYMENT/.clone.sqfs"
  rm -f "$KESSEL_DEPLOYMENT/.*.sqfs" # remove any legacy sqfs files
  "$KESSEL_ROOT/lib/kessel/workflows/base/spack/deployment/gen_clone_sqfs" "$KESSEL_DEPLOYMENT" "$SQFS_FILE"
  chown ":$KESSEL_GROUP" "$SQFS_FILE"
  chmod "$KESSEL_PERMISSIONS" "$SQFS_FILE"
fi

echo "Setting permissions and group of spack/opt/spack ..."
chown -R ":$KESSEL_GROUP" "$KESSEL_DEPLOYMENT/spack/opt/spack"
chmod -R "$KESSEL_PERMISSIONS" "$KESSEL_DEPLOYMENT/spack/opt/spack"
if [ -d "$_SPACK_DB_DIR" ]; then
  chmod g+s "$_SPACK_DB_DIR"
fi

unset _SPACK_DB_DIR
