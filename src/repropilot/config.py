from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # LLM provider settings
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"  # change if you want
    temperature: float = 0.2
    max_tokens: int = 800

    # Memory & logs
    workspace_dir: str = "workspace"
    sqlite_path: str = "workspace/repropilot.sqlite3"

    # Safety: restrict shell tool to allow-listed commands only
    enable_shell_tool: bool = True


def get_settings() -> Settings:
    return Settings()
