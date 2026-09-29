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

import argparse
import json
import re
import shutil
import socket
import subprocess

from pathlib import Path


def detect_system_name():
    """Detect the current cluster name"""
    if shutil.which("sacctmgr"):
        return json.loads(subprocess.check_output(["sacctmgr", "list", "--json", "clusters"]))['clusters'][0]['name']
    if shutil.which("flux"):
        return re.sub(r'[0-9]+', "", socket.gethostname())
    return None


def detect_batch_system():
    """Detect batch system on a cluster"""
    if shutil.which("sacctmgr"):
        return "slurm"
    if shutil.which("flux"):
        return "flux"
    return None


def deployment_environments(deployment_dir : Path | str) -> List[str]:
    """Return all available Spack environment in a given deployment"""
    env_dir = Path(deployment_dir) / "environments"
    return [str(p.parent.relative_to(env_dir)) for p in env_dir.rglob("spack.yaml") if p.is_file()]


def alloc_main(prog_name, exports, params_callback):
    parser = argparse.ArgumentParser(prog=prog_name, description=("Allocate a compute node for a given Spack environment via the job scheduler."))

    parser.add_argument(
        "--persist",
        metavar="PATH",
        help=(
            "keep a reusable writable deployment at PATH instead of a "
            "temporary per-user copy (sets KESSEL_WORKFLOW_DEPLOYMENT)"
        ),
    )
    parser.add_argument(
        "--print-params",
        action="store_true",
        help=(
            "print the resolved scheduler parameters for SPACK_ENV_NAME and exit "
            "without allocating"
        ),
    )
    parser.add_argument(
        "spack_env_name",
        metavar="SPACK_ENV_NAME",
        help="Spack environment to allocate for",
    )
    parser.add_argument(
        "scheduler_args",
        metavar="extra scheduler args",
        nargs=argparse.REMAINDER,
        help="additional arguments passed to the scheduler",
    )
    args = parser.parse_args()
    return 0
