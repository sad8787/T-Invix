from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)
    bot_token: str
    mini_app_url: str = "https://example.com"
    api_url: str = "http://backend:8000"\n    internal_api_token: str = "replace-this-internal-token"
    admin_telegram_ids: str = ""
    bot_mode: str = "webhook"
    webhook_path: str = "/telegram/webhook"
    webhook_secret: str = "replace-with-a-long-random-secret"
    webhook_host: str = "0.0.0.0"
    webhook_port: int = 8081
    webhook_public_url: str = ""

    @property
    def admin_ids(self) -> set[int]:
        return {int(value.strip()) for value in self.admin_telegram_ids.split(",") if value.strip()}

settings = Settings()