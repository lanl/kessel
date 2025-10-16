#KESSEL title: Submit
(
source "$KESSEL_BUILD_ENV"
cmake --build "$KESSEL_BUILD_DIR" --target install
)
