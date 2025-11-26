#KESSEL title: Autoformat
(
source "$KESSEL_BUILD_ENV"
python3 -m autopep8 -iaar --max-line-length 120 "$KESSEL_SOURCE_DIR/lib"
)
