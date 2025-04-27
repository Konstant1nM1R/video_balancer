from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://pos:pos@localhost:5432/vid"
    CDN_HOST: str = "cdn.example.com"
    REDIRECT_RATIO: int = 5  
    
    class Config:
        env_file = ".env"

settings = Settings() 