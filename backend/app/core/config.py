from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI 旅行记忆助手"
    env: str = "development"
    database_url: str = "sqlite:///./data/travel_memory.db"
    vivo_app_key: str = ""
    vivo_api_base: str = "https://api-ai.vivo.com.cn/v1"
    vivo_model: str = "Doubao-Seed-2.0-mini"
    vivo_image_model: str = "Doubao-Seedream-4.5"
    vivo_mock_when_no_key: bool = True
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
