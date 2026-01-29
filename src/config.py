from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pydantic import Field

class Settings(BaseSettings):
    db_url: str = Field(alias="DATABASE_URL")
    mia_api_key: str = "test_key"
    firebase_credentials_path: str = ""
    public_site_base_url: str = "https://webecommerce-250878482242.asia-southeast1.run.app/s"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()
