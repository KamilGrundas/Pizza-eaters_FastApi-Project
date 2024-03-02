from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_port: int

    sqlalchemy_database_url: str

    host: str
    port: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # to powoduje że nie wywali się gdy jakieś zmienne nie zostaną wykorzystane


settings = Settings()
