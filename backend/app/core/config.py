import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "TrackNet / NSIS - National Sports Intelligence System"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./tracknet.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "tracknet-sovereign-dev-secret-key-32charsmin!")
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "kZ45G62zZ0K1l8Q47N7yX9wP2vM5aB8cE1fH3jK5mO8=")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    SMALL_CELL_THRESHOLD: int = 5
    GAP_RATIO_THRESHOLD: float = 0.50

    class Config:
        case_sensitive = True

settings = Settings()
