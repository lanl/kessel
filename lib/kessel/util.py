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

import os
import shlex
import subprocess
import sys
from io import TextIOWrapper
from pathlib import Path
from typing import TextIO

from kessel.colors import COLOR_CYAN, COLOR_PLAIN


def create_squashfs(src: str, dest: str) -> None:
    print(f"Creating squashfs file {dest}...")
    subprocess.run(["mksquashfs", src, dest, "-comp", "gzip"])


def symbolic_to_octal(perm_str: str, directory: bool = False) -> int:
    perm_bits = {"r": 4, "w": 2, "x": 1}
    perms = {"u": 0, "g": 0, "o": 0}

    for clause in perm_str.split(","):
        who, rights = clause.split("=")
        bit = 0
        for char in rights:
            if char in perm_bits:
                bit |= perm_bits[char]
            elif char == "X" and directory:
                bit |= perm_bits["x"]
        perms[who] = bit

    return int(f"{perms['u']}{perms['g']}{perms['o']}", 8)


class ShellEnvironment(object):
    def __init__(self) -> None:
        try:
            self.fd: TextIOWrapper = open(3, "w", closefd=False)
        except OSError:
            print("ERROR: Current shell is misconfigured. Reload kessel into current shell.", file=sys.stderr)
            sys.exit(1)
        self.debug: bool = False
        self._collapsed_sections: set[str] = set()

    @property
    def target(self) -> TextIO | TextIOWrapper:
        return sys.stdout if self.debug else self.fd

    def eval(self, cmd: str, *args: str | Path, end: str = "\n") -> None:
        a = " ".join([shlex.quote(str(a)) for a in args])
        if os.getenv("IN_FISH") is not None:
            print(f"{cmd} {a}; or return", file=self.target, flush=True, end=end)
        else:
            print(f"{cmd} {a} || return", file=self.target, flush=True, end=end)

    def set_env_var(self, name: str, value: str | None) -> None:
        if value is None:
            self.unset_env_var(name)
            return
        if os.getenv("IN_FISH") is not None:
            self.eval(f"set -g {name} {shlex.quote(str(value))}")
        else:
            self.eval(f"export {name}={shlex.quote(str(value))}")
        os.environ[name] = str(value)

    def __contains__(self, key: str) -> bool:
        return key in os.environ

    def __getitem__(self, key: str) -> str:
        if key not in os.environ:
            raise KeyError(f"Environment variable '{key}' is not defined.")
        return os.environ[key]

    def __setitem__(self, key: str, value: str | None) -> None:
        self.set_env_var(key, value)

    def get(self, key: str, default: str | None = None) -> str | None:
        if key not in self:
            return default
        return self[key]

    def unset_env_var(self, name: str) -> None:
        if os.getenv("IN_FISH") is not None:
            self.eval(f"set -e {name}")
        else:
            self.eval(f"unset {name}")
        if name in os.environ:
            del os.environ[name]

    def source(self, path: str | Path, *args: str) -> None:
        self.eval("source", path, *args)

    def echo(self, msg: str = "") -> None:
        for line in msg.splitlines():
            self.eval("echo", line)

    def _is_github_actions(self) -> bool:
        """Check if running on GitHub Actions."""
        return "GITHUB_ACTIONS" in os.environ and os.environ["GITHUB_ACTIONS"] == "true"

    def _is_gitlab_ci(self) -> bool:
        """Check if running on GitLab CI."""
        return "GITLAB_CI" in os.environ

    def _section(self, marker: str, section: str, passthrough: bool = False, msg: str = "") -> None:
        if self._is_gitlab_ci():
            if passthrough:
                print(
                    f"\033[0Ksection_{marker}:$(date +%s):{section}\r\033[0K{COLOR_CYAN}{msg}{COLOR_PLAIN}",
                    flush=True,
                )
            else:
                self.eval(
                    f'echo -e "\033[0Ksection_{marker}:$(date +%s):{section}\r\033[0K{COLOR_CYAN}{msg}{COLOR_PLAIN}"'
                )
        else:
            if passthrough:
                print(f"{COLOR_CYAN}{msg}{COLOR_PLAIN}", flush=True)
            else:
                self.eval(f'echo -e "{COLOR_CYAN}{msg}{COLOR_PLAIN}"')

    def section_start(self, section: str, msg: str, collapsed: bool = False, passthrough: bool = False) -> None:
        if self._is_github_actions():
            if collapsed:
                self._collapsed_sections.add(section)
                if passthrough:
                    print(f"::group::{msg}", flush=True)
                else:
                    self.eval(f'echo "::group::{msg}"')
            else:
                if passthrough:
                    print(f"{COLOR_CYAN}{msg}{COLOR_PLAIN}", flush=True)
                else:
                    self.eval(f'echo -e "{COLOR_CYAN}{msg}{COLOR_PLAIN}"')
        elif self._is_gitlab_ci():
            if collapsed:
                section += "[collapsed=true]"
            self._section("start", section, passthrough, msg)
        else:
            if passthrough:
                print(f"{COLOR_CYAN}{msg}{COLOR_PLAIN}", flush=True)
            else:
                self.eval(f'echo -e "{COLOR_CYAN}{msg}{COLOR_PLAIN}"')

    def section_end(self, section: str, passthrough: bool = False) -> None:
        if self._is_github_actions():
            if section in self._collapsed_sections:
                self._collapsed_sections.remove(section)
                if passthrough:
                    print("::endgroup::", flush=True)
                else:
                    self.eval('echo "::endgroup::"')
        elif self._is_gitlab_ci():
            self._section("end", section, passthrough)
