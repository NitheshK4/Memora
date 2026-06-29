import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./memora.db"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    RATE_LIMIT_MAX_REQUESTS: int = 60
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    
    @property
    def is_openai_configured(self) -> bool:
        """Returns True if the OpenAI API Key is set to a non-empty value."""
        return bool(self.OPENAI_API_KEY and self.OPENAI_API_KEY.strip())

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


settings = Settings()
