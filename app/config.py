"""
Loads configuration from the .env file.

Everything sensitive (database URL, OpenAI key, secret key) lives in .env
on your machine and is read here ONCE at startup. If a required value is
missing, the app refuses to start instead of failing later at runtime.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Tells pydantic to read from a file called .env in the project root.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # "development" or "production". Used later to change behaviour
    # (e.g. showing detailed errors only in development).
    ENVIRONMENT: str = "development"

    # Signs session cookies so a user cannot forge someone else's login.
    SECRET_KEY: str

    # How the app connects to Postgres. Read from .env.
    DATABASE_URL: str

    # Your OpenAI key. Read from .env, never hard-coded.
    OPENAI_API_KEY: str = ""


# A single shared settings object the rest of the app imports.
settings = Settings()
