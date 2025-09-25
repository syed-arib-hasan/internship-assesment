from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///sms.db"

    class Config:
        env_file = ".env"

settings = Settings()
