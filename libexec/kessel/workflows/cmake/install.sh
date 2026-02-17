(
if [ -f "$KESSEL_BUILD_ENV" ]; then
  source "$KESSEL_BUILD_ENV"
fi
cmake --build "$KESSEL_BUILD_DIR" --target install
)
