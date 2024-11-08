from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DEBUG: bool
    SECRET_KEY: str

    class Config:
        env_file = '.env'


settings = Settings()