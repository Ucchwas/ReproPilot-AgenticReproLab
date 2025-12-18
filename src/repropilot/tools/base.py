from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Protocol
from pydantic import BaseModel


class Tool(Protocol):
    name: str
    description: str
    Args: type[BaseModel]
    def run(self, args: BaseModel) -> str: ...


@dataclass
class ToolRegistry:
    tools: dict[str, Tool]

    def list_for_prompt(self) -> str:
        lines = []
        for t in self.tools.values():
            schema = t.Args.model_json_schema()
            lines.append(f"- {t.name}: {t.description}\n  args_schema={schema}")
        return "\n".join(lines)
