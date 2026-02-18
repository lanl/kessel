source "${KESSEL_DEPLOYMENT}/activate.sh"

if ! spack bootstrap status; then
    spack bootstrap now
    spack bootstrap status
fi
