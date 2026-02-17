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

(
if [ -f "$KESSEL_BUILD_ENV" ]; then
  source "$KESSEL_BUILD_ENV"
fi
export CTEST_OUTPUT_ON_FAILURE=1
ctest --timeout "${CTEST_TIMEOUT:-600}" --test-dir "$KESSEL_BUILD_DIR" --output-junit tests.xml "$@"
)
