#KESSEL title: Type checking
(
source "$KESSEL_BUILD_ENV"
python3 -m mypy "$KESSEL_SOURCE_DIR/lib"
)
