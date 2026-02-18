concretize_env_for_mirror() {
    env_name="$1"
    echo "Concretizing $env_name..."
    spack env activate $env_name
    rm -rf "$SPACK_ENV/.spack-env"
    mkdir -p "$SPACK_ENV/.spack-env"
    cp "$SPACK_ENV/spack.yaml" "$SPACK_ENV/spack.yaml.original"

    spack config add view:false

    spack concretize -f --fresh 2>&1 > "$SPACK_ENV/.spack-env/concretization.txt" || touch "$SPACK_ENV/.spack-env/failure" &
    spack env deactivate
}

get_env_name() {
    absolute_path=$(readlink -f "$1")
    abs_root=$(readlink -f "$2")
    realpath -s "$(dirname "$absolute_path")" | sed "s|^$abs_root/||"
}

create_env_mirror() {
    mirror_dir="$1"
    mirror_exclude_file="$2"
    env_name="$3"
    failure_file="$SPACK_ENV/.spack-env/failure"
    if [ -f "$failure_file" ]; then
        echo "ERROR: Concretization of $env_name failed!" >&2
        return 1
    else
        echo "Creating mirror for $env_name..."
        spack env activate $env_name
        spack spec
        if [ -f "$SPACK_ENV/spack.lock" ]; then
            if [ -f "$mirror_exclude_file" ]; then
                spack mirror create -d "$mirror_dir" --all --skip-unstable-version --exclude-file "$mirror_exclude_file"
            else
                spack mirror create -d "$mirror_dir" --all --skip-unstable-version
            fi
        else
            echo "SKIPPING $env_name due to missing concrete specs."
        fi
        rm -f "$SPACK_ENV/spack.lock"
        cp "$SPACK_ENV/spack.yaml.original" "$SPACK_ENV/spack.yaml"
    fi
}

if [ -z "${ENVIRONMENTS}" ]; then
    export ENVIRONMENTS="$(spack env list | tr -d ' ')"
fi

mirror_dir="$KESSEL_DEPLOYMENT/spack-mirror"
env_dir="$KESSEL_DEPLOYMENT/environments/$KESSEL_SYSTEM"

set +m

printf "%s\n" "$ENVIRONMENTS" | while IFS= read -r e
do
    if [ -n "${e}" ]; then
        concretize_env_for_mirror "$e"
    fi
done

wait

set -m

printf "%s\n" "$ENVIRONMENTS" | while IFS= read -r e
do
    if [ -n "${e}" ]; then
        create_env_mirror "$mirror_dir" "$mirror_exclude_file" "$e"
    fi
done
