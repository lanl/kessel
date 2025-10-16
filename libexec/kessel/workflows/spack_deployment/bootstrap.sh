kessel deploy activate "$KESSEL_DEPLOYMENT"
kessel system activate "$KESSEL_SYSTEM"

export KESSEL_REQUIRE_SYSTEM_MIRROR=none
if [ "$KESSEL_SYSTEM" = "rocinante"  ] || [ "$KESSEL_SYSTEM" = "ATS3" ]; then
    export KESSEL_REQUIRE_SYSTEM_MIRROR="pe-serve"
fi

spack bootstrap status || true
spack bootstrap now
spack bootstrap status
spack bootstrap mirror --binary-packages "${KESSEL_DEPLOYMENT}/spack-bootstrap" || true

unset KESSEL_REQUIRE_SYSTEM_MIRROR
