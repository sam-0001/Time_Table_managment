import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "School Timetable Management System"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "b304c4dbb9b6e22f28148b8b9dc1e089d81d2f8e1248c89b2d8e6a2134567890") # Use a strong key in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 365 # 1 year for development
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")

settings = Settings()
