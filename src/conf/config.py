from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_port: int

    cloud_name: str
    api_key: str
    api_secret: str

    sqlalchemy_database_url: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
