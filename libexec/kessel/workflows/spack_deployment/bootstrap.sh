kessel deploy activate "$KESSEL_DEPLOYMENT"

export KESSEL_REQUIRE_SYSTEM_MIRROR=none
if [ "$KESSEL_SYSTEM" = "rocinante"  ] || [ "$KESSEL_SYSTEM" = "ATS3" ] || [ "$KESSEL_SYSTEM" = "selene" ]; then
    export KESSEL_REQUIRE_SYSTEM_MIRROR="pe-serve"
fi

if ! spack bootstrap status; then
    spack bootstrap now
    spack bootstrap status
fi