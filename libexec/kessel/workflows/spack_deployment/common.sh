copy_configuration() {
  mkdir -p "$KESSEL_DEPLOYMENT/config"

  rsync -av --include="/config/" --include='/config/*.yaml' \
            --include='/config/templates/' --include='/config/templates/**' \
            --exclude='*' "$KESSEL_DEPLOYMENT_CONFIG/" "$KESSEL_DEPLOYMENT/"

  if [ -d "$KESSEL_DEPLOYMENT_CONFIG/config/$KESSEL_SYSTEM" ]; then
    # might be a symlink
    system_config_dir=$(basename $(realpath $KESSEL_DEPLOYMENT_CONFIG/config/$KESSEL_SYSTEM))

    rsync -av --include="/config/$system_config_dir/" --include="/config/$system_config_dir/"'**' \
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
  mkdir -p "$KESSEL_DEPLOYMENT/environments"
  for env in $(find "$KESSEL_DEPLOYMENT_CONFIG/environments/$KESSEL_SYSTEM" -iname '*.yaml'); do
    env_file=$(echo $env | sed -e "s%^$KESSEL_DEPLOYMENT_CONFIG/environments/$KESSEL_SYSTEM/%%")
    env_dir=${env_file%.*}
    mkdir -p "${KESSEL_DEPLOYMENT}/environments/$env_dir"
    cp "$env" "${KESSEL_DEPLOYMENT}/environments/$env_dir/spack.yaml"
  done
}
