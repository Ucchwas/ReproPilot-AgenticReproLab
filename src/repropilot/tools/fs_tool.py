from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from pydantic import BaseModel, Field


class WriteFileArgs(BaseModel):
    path: str = Field(..., description="File path to write")
    content: str = Field(..., description="Content to write")
    overwrite: bool = Field(default=False, description="Overwrite if exists")


@dataclass
class WriteFileTool:
    name: str = "write_file"
    description: str = "Writes a file to disk (creates directories as needed)."
    Args = WriteFileArgs

    def run(self, args: WriteFileArgs) -> str:
        p = Path(args.path)
        p.parent.mkdir(parents=True, exist_ok=True)
        if p.exists() and not args.overwrite:
            return f"SKIP: {p} exists (overwrite=false)"
        p.write_text(args.content, encoding="utf-8")
        return f"WROTE: {p}"
