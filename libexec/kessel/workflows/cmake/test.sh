(
if [ -f "$KESSEL_BUILD_ENV" ]; then
  source "$KESSEL_BUILD_ENV"
fi
export CTEST_OUTPUT_ON_FAILURE=1
ctest --timeout "${CTEST_TIMEOUT:-600}" --test-dir "$KESSEL_BUILD_DIR" --output-junit tests.xml "$@"
)
