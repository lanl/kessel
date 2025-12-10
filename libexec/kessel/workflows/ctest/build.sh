(
source "$KESSEL_BUILD_ENV"
ctest -VV -S $KESSEL_CTEST_DRIVER_SCRIPT,Configure,Build,$report_errors
)
