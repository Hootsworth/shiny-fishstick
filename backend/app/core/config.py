import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Shiny Fishstick"
    # SQLite default database path, switchable to postgresql via env
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./preflight.db")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

settings = Settings()
