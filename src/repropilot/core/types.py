from __future__ import annotations
from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    type: str = Field("tool")
    tool: str
    args: dict


class FinalAnswer(BaseModel):
    type: str = Field("final")
    message: str
