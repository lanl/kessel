(
if [ -f "$KESSEL_BUILD_ENV" ]; then
  source "$KESSEL_BUILD_ENV"
fi
cmake "$@" "$KESSEL_BUILD_DIR"
cmake --build "$KESSEL_BUILD_DIR" --parallel
)
