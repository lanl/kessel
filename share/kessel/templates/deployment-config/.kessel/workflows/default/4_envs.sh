#KESSEL title: Build environments

if [ "$KESSEL_SYSTEM" = "rocinante"  ] || [ "$KESSEL_SYSTEM" = "ATS3" ] || [ "$KESSEL_SYSTEM" = "rzadams"  ] || [ "$KESSEL_SYSTEM" = "rzvernal"  ] || [ "$KESSEL_SYSTEM" = "ATS4" ]; then
    export KESSEL_REQUIRE_GIT_MIRRORS=true
fi

if [ -n "$PROJECT" ] && [ -n "$PROJECT_ENVIRONMENTS" ]; then
  ENVIRONMENTS=""
  printf "%s\n" "$PROJECT_ENVIRONMENTS" | while IFS= read -r e
  do
    ENVIRONMENTS="$ENVIRONMENTS$PROJECT/$e"
  done
  export ENVIRONMENTS="${ENVIRONMENTS# }"
else
  export ENVIRONMENTS="${ENVIRONMENTS:-$(spack env list | tr -d ' ')}"
fi

echo "Building these environments:"
echo "${ENVIRONMENTS}"
echo

source "$KESSEL_ROOT/libexec/kessel/workflows/spack_deployment/envs"
