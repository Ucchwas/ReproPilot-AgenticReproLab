from __future__ import annotations

from openai import OpenAI
from repropilot.llm.base import ChatModel, LLMResponse
from repropilot.config import Settings


class OpenAIChatModel(ChatModel):
    def __init__(self, settings: Settings):
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is missing. Put it in .env (not committed).")
        self._client = OpenAI(api_key=settings.openai_api_key)
        self._model = settings.openai_model
        self._temp = settings.temperature
        self._max = settings.max_tokens

    def generate(self, system: str, user: str) -> LLMResponse:
        resp = self._client.chat.completions.create(
            model=self._model,
            temperature=self._temp,
            max_tokens=self._max,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return LLMResponse(text=resp.choices[0].message.content or "")
