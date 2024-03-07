from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_port: int

    sqlalchemy_database_url: str

    cloud_name: str
    api_key: str
    api_secret: str

    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int
    mail_server: str
    secret_key: str
    algorithm: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # to powoduje że nie wywali się gdy jakieś zmienne nie zostaną wykorzystane


settings = Settings()
