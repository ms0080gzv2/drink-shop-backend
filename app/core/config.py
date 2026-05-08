from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    redis_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080
    line_channel_secret: str = ""
    line_channel_access_token: str = ""
    line_login_channel_id: str = ""
    line_login_channel_secret: str = ""
    admin_default_email: str = ""
    admin_default_password: str = ""
    allowed_origins: str = "http://localhost:3000"

    class Config:
        env_file = ".env"

settings = Settings()
