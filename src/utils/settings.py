from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
  model_config = SettingsConfigDict(env_file=".env", extra="ignore")
  DB_CONNECTION: str
  SECRET_KEY: str
  ALGORITHM: str
  ACCESS_TOKEN_EXPIRY_MINUTES: int
  REFRESH_TOKEN_EXPIRY_DAYS: int

settings = Settings()