(
if [ -f "$KESSEL_BUILD_ENV" ]; then
  source "$KESSEL_BUILD_ENV"
fi
ctest -V -S $KESSEL_CTEST_DRIVER_SCRIPT,Submit
)
