umask 0007

if [[ ! -d "$KESSEL_DEPLOYMENT" ]]; then
  if [[ -z "$SPACK_ROOT" ]]; then
    echo "ERROR: No active Spack installation!" >&2
    return 1
  else
    echo "Using Spack install at $SPACK_ROOT"
  fi
fi
