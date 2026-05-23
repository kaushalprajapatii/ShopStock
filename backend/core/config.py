from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/inventory_db"
    SECRET_KEY: str = "changethiskey"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ADMIN_EMAIL: str = "admin@shop.com"
    ADMIN_PASSWORD: str = "admin123"

    class Config:
        env_file = ".env"

settings = Settings()
