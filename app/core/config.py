
from pydantic_settings import BaseSettings , SettingsConfigDict 
from pydantic import field_validator



class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    JWT_SECRET: str
    
    
    @field_validator("DATABASE_URL" )
    def validate_db(cls , value):
        if not value.startswith("postgresql"):
            raise ValueError("Only postgresql database alloed")
        return value
    
    
    
    
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )
        
settings = Settings()