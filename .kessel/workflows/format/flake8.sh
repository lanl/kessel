(
source "$KESSEL_BUILD_ENV"
python3 -m flake8 --max-line-length 120 --ignore=F401,E226,W503,W504 "$KESSEL_SOURCE_DIR/lib"
)
