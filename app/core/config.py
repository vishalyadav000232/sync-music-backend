from pydantic import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    JWT_SECRET: str
    
    class config:
        env_file = ".env"
        
settings = Settings()