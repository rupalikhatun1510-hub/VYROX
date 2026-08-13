from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    ENVIRONMENT: str = "development"
    SECRET_KEY: str
    DATABASE_URL: str
    OPENAI_API_KEY: str = ""

settings = Settings()
