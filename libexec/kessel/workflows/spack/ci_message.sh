export KESSEL_PROJECT_NAME=$(spack-python -c "spec = spack.spec.Spec('$KESSEL_PROJECT_SPEC');print(spec.name)")
kessel_ci_message "$KESSEL_PROJECT_NAME" "$KESSEL_CURRENT_SYSTEM" "$KESSEL_INIT" "$KESSEL_WORKFLOW" "$@"
