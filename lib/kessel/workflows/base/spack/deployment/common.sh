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

copy_configuration() {
  rsync -av --include="/config/" --include='/config/*.yaml' \
            --include='/config/templates/' --include='/config/templates/**' \
            --exclude='*' "$KESSEL_DEPLOYMENT_CONFIG/" "$KESSEL_DEPLOYMENT/"

  echo "$KESSEL_DEPLOYMENT_CONFIG/config/$KESSEL_SYSTEM"

  if [ -d "$KESSEL_DEPLOYMENT_CONFIG/config/$KESSEL_SYSTEM" ]; then
    # might be a symlink
    system_config_dir=$(basename $(realpath $KESSEL_DEPLOYMENT_CONFIG/config/$KESSEL_SYSTEM))

    rsync -av --include="/config/" \
              --include="/config/$system_config_dir/" --include="/config/$system_config_dir/"'**' \
              --exclude='*' "$KESSEL_DEPLOYMENT_CONFIG/" "$KESSEL_DEPLOYMENT/"

    # copy symlinks to share same configuration
    for f in $(find $KESSEL_DEPLOYMENT_CONFIG/config -maxdepth 1 -type l); do
      if [ "$(basename $(realpath $f))" == "$system_config_dir" ]; then
        target_link="$KESSEL_DEPLOYMENT/config/$(basename $f)"
        rm -rf $target_link
        ln -s $system_config_dir $target_link
      fi
    done
  fi
}

generate_environments() {
  echo "Creating $KESSEL_DEPLOYMENT/environments"
  mkdir -p "$KESSEL_DEPLOYMENT/environments"
  for env in $(find -L "$KESSEL_DEPLOYMENT_CONFIG/environments/$KESSEL_SYSTEM" -iname '*.yaml'); do
    env_file=$(echo $env | sed -e "s%^$KESSEL_DEPLOYMENT_CONFIG/environments/$KESSEL_SYSTEM/%%")
    env_dir=${env_file%.*}
    echo "Creating $KESSEL_DEPLOYMENT/environments/$env_dir"
    mkdir -p "${KESSEL_DEPLOYMENT}/environments/$env_dir"
    cp "$env" "${KESSEL_DEPLOYMENT}/environments/$env_dir/spack.yaml"
  done
}
