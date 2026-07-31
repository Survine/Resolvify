from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://resolvify_user:resolvify_pass@localhost:5432/resolvify_db"
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "*",
    ]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
