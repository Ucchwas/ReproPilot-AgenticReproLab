from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class LLMResponse:
    text: str


class ChatModel(Protocol):
    def generate(self, system: str, user: str) -> LLMResponse: ...
