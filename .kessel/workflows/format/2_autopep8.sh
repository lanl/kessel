#KESSEL title: Autoformat
(
source "$KESSEL_BUILD_ENV"
python3 -m autopep8 -iaar --max-line-length 120 --exclude _vendoring "$KESSEL_SOURCE_DIR/lib"
)
