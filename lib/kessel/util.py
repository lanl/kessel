import os
import subprocess
import shlex
import sys
from typing import TextIO
from io import TextIOWrapper
from pathlib import Path

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
        self.fd: TextIOWrapper = open(3, "w", closefd=False)
        self.debug: bool = False

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

    def __setitem__(self, key: str, value: str) -> None:
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

    def echo(self, str: str = "") -> None:
        for line in str.splitlines():
            self.eval("echo", line)

    def _section(self, marker: str, section: str, passthrough: bool = False,
                 msg: str = "") -> None:
        if "CI" in os.environ:
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
        if "CI" in os.environ:
            if collapsed:
                section += "[collapsed=true]"

        self._section("start", section, passthrough, msg)

    def section_end(self, section: str, passthrough: bool = False) -> None:
        self._section("end", section, passthrough)
