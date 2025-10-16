#KESSEL title: Linting
(
source "$KESSEL_BUILD_ENV"
python3 -m flake8 --max-line-length 120 --exclude _vendoring --ignore=F401,E226,W503,W504 "$KESSEL_SOURCE_DIR/lib"
)
