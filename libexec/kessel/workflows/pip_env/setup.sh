ENV_DIR="$KESSEL_BUILD_DIR/envs"
ENV="$ENV_DIR/$KESSEL_PIP_ENV"
mkdir -p "$ENV_DIR"

if [ ! -d "$ENV" ]; then
    "$KESSEL_PYTHON" -m venv "$ENV"
fi

source "$ENV/bin/activate"

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate environment" >&2
    return 1
fi

python3 -m pip install -r "$KESSEL_REQUIREMENTS"
deactivate

export KESSEL_BUILD_ENV=${ENV}/bin/activate
