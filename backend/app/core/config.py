from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)
    database_url: str = "postgresql+asyncpg://catalog:catalog@postgres:5432/catalog"
    minio_endpoint: str = "minio:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "catalog-images"
    minio_secure: bool = False
    minio_public_url: str = "http://localhost:9000"
    cors_origins: list[str] = ["*"]
    max_upload_bytes: int = 10 * 1024 * 1024
    admin_telegram_ids: str = ""
    internal_api_token: str = "replace-this-internal-token"

    @property
    def admin_ids(self) -> set[int]:
        return {int(value.strip()) for value in self.admin_telegram_ids.split(",") if value.strip()}

settings = Settings()
