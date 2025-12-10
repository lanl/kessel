import os
import subprocess
import sys

from kessel.cmd.workflow import COLOR_CYAN, COLOR_PLAIN


def create_squashfs(src, dest):
    print(f"Creating squashfs file {dest}...")
    subprocess.run(["mksquashfs", src, dest, "-comp", "gzip"])


def symbolic_to_octal(perm_str, directory=False):
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
    def __init__(self):
        self.fd = open(3, "w", closefd=False)
        self.debug = False

    @property
    def target(self):
        return sys.stdout if self.debug else self.fd

    def eval(self, cmd, end="\n"):
        if os.getenv("IN_FISH") is not None:
            print(f"{cmd}; or return", file=self.target, flush=True, end=end)
        else:
            print(f"{cmd} || return", file=self.target, flush=True, end=end)

    def set_env_var(self, name, value):
        if value is None:
            self.unset_env_var(name)
            return
        if os.getenv("IN_FISH") is not None:
            self.eval(f"set -g {name} {value}")
        else:
            self.eval(f"export {name}={value}")
        os.environ[name] = str(value)

    def __contains__(self, key):
        return key in os.environ

    def __getitem__(self, key):
        if key not in os.environ:
            raise KeyError(f"Environment variable '{key}' is not defined.")
        return os.environ[key]

    def __setitem__(self, key, value):
        self.set_env_var(key, value)

    def get(self, key, default=None):
        if key not in self:
            return default
        return self[key]

    def unset_env_var(self, name):
        if os.getenv("IN_FISH") is not None:
            self.eval(f"set -e {name}")
        else:
            self.eval(f"unset {name}")
        if name in os.environ:
            del os.environ[name]

    def source(self, path):
        self.eval(f"source {path}")

    def echo(self, str=""):
        for line in str.splitlines():
            self.eval(f"echo '{line}'")

    def _section(self, marker, section, passthrough=False, msg=""):
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

    def section_start(self, section, msg, collapsed=False, passthrough=False):
        if "CI" in os.environ:
            if collapsed:
                section += "[collapsed=true]"

        self._section("start", section, passthrough, msg)

    def section_end(self, section, passthrough=False):
        self._section("end", section, passthrough)
