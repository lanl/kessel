copy_configuration() {
  mkdir -p "$KESSEL_DEPLOYMENT/config"
  rsync -av --include="/config/" --include='/config/*.yaml' \
            --include='/config/templates/' --include='/config/templates/**' \
            --include="/config/$KESSEL_SYSTEM/" --include="/config/$KESSEL_SYSTEM/"'**' \
            --exclude='*' "$KESSEL_DEPLOYMENT_CONFIG/" "$KESSEL_DEPLOYMENT/"
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
