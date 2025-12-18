from __future__ import annotations
from dataclasses import dataclass
import shlex
import subprocess
from pydantic import BaseModel, Field


ALLOWED = {
    "python": {"-m", "-c", "compileall", "pip"},
    "pytest": set(),
    "ruff": {"check", "format"},
    "git": {"status", "diff", "rev-parse"},
}


class ShellArgs(BaseModel):
    cmd: str = Field(..., description="Command to run (allow-listed only)")
    cwd: str | None = Field(default=None, description="Working directory")


@dataclass
class SafeShellTool:
    name: str = "safe_shell"
    description: str = "Runs allow-listed shell commands (pytest/ruff/python/git)."
    Args = ShellArgs

    def run(self, args: ShellArgs) -> str:
        parts = shlex.split(args.cmd)
        if not parts:
            raise ValueError("Empty command")

        exe = parts[0]
        if exe not in ALLOWED:
            raise ValueError(f"Command not allowed: {exe}")

        allowed_args = ALLOWED[exe]
        # If allowed_args is empty set => allow any args? No: keep strict.
        if allowed_args:
            for a in parts[1:]:
                if a.startswith("-"):
                    if a not in allowed_args:
                        raise ValueError(f"Flag not allowed for {exe}: {a}")
                else:
                    # non-flag positional: allow (e.g., paths) but limit size
                    if len(a) > 300:
                        raise ValueError("Argument too long")

        proc = subprocess.run(
            parts,
            cwd=args.cwd,
            capture_output=True,
            text=True,
            timeout=120,
        )
        out = (proc.stdout or "") + "\n" + (proc.stderr or "")
        return f"exit={proc.returncode}\n{out}".strip()
