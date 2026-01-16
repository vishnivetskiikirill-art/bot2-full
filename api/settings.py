from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Railway обычно отдаёт DATABASE_URL / или POSTGRES_URL — оставляем DATABASE_URL
    DATABASE_URL: str

    # логин/пароль для /admin
    ADMIN_USER: str = "admin"
    ADMIN_PASS: str = "admin"

    # секрет для сессий (поставь длинную строку в Railway ENV)
    SESSION_SECRET: str = "CHANGE_ME_SUPER_LONG_RANDOM"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
