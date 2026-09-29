#!/bin/bash
# © 2026. Triad National Security, LLC. All rights reserved.
# This program was produced under U.S. Government contract 89233218CNA000001
# for Los Alamos National Laboratory (LANL), which is operated by Triad
# National Security, LLC for the U.S.  Department of Energy/National Nuclear
# Security Administration. All rights in the program are reserved by Triad
# National Security, LLC, and the U.S. Department of Energy/National Nuclear
# Security Administration. The Government is granted for itself and others
# acting on its behalf a nonexclusive, paid-up, irrevocable worldwide license
# in this material to reproduce, prepare derivative works, distribute copies to
# the public, perform publicly and display publicly, and to permit others to do
# so.
#
# Wrapper handed to salloc/flux alloc as $SHELL by kessel_alloc. It runs inside
# the allocation to activate the workflow deployment (creating a writable copy
# only if one doesn't already exist) using KESSEL_DEPLOYMENT inherited from the
# allocating shell, then hands off to a login bash.

source "$KESSEL_DEPLOYMENT/kessel/lib/kessel/workflows/base/spack/deployment/use.sh"
kessel_activate_deployment || exit $?

export SHELL=/bin/bash
export -f kessel

KESSEL_VERSION=$(cat "$KESSEL_WORKFLOW_DEPLOYMENT/.kessel_version" 2>/dev/null)

BOLD='\033[1m'
RESET='\033[0m'

echo
echo -e "${BOLD}Spack deployment and Kessel${KESSEL_VERSION:+ ($KESSEL_VERSION)} are now available${RESET}"
echo
echo "Common commands:"
echo
echo -e "${BOLD}spack env list${RESET}    show available environments"
echo -e "${BOLD}kessel run${RESET}        run workflow with $KESSEL_SPACK_ENV Spack environment"
echo -e "${BOLD}kessel status${RESET}     show current workflow state"
echo -e "${BOLD}kessel build-env${RESET}  enter build and run environment (requires completed configure step)"
echo

exec /bin/bash -l
