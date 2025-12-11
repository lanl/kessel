umask 0007

if [[ ! -d "$KESSEL_DEPLOYMENT" ]]; then
  if [[ -z "$SPACK_ROOT" ]]; then
    echo "ERROR: No active Spack installation!" >&2
    return 1
  else
    echo "Using Spack install at $SPACK_ROOT"
  fi
fi

export KESSEL_PROJECT_NAME=$(spack-python -c "spec = spack.spec.Spec('$KESSEL_PROJECT_SPEC');print(spec.name)")
kessel_ci_message "$KESSEL_PROJECT_NAME" "$KESSEL_CURRENT_SYSTEM" "$KESSEL_INIT" "$KESSEL_WORKFLOW" "$FULL_ARGS"
