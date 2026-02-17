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
