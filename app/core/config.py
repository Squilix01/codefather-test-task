from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from sqlalchemy import URL


class DatabaseConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    user: str = Field(alias="DB_USER")
    password: str = Field(alias="DB_PASSWORD")
    db_name: str = Field(alias="DB_NAME")
    host: str = Field(alias="DB_HOST")
    port: int = Field(alias="DB_PORT")

    def get_database_url(self, DB_API: str) -> URL:
        return URL.create(
            drivername=f"postgresql+{DB_API}",
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.db_name,
        )
    
    
class JWTConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    secret_key: str = Field(alias="SECRET_KEY")
    algorithm: str = Field(alias="ALGORITHM")
    access_token_expire_minutes: int = Field(alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(alias="REFRESH_TOKEN_EXPIRE_DAYS")


class RabbitMQConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    rabbitmq: str = Field(alias="RABBITMQ_URL")


class Config:
    def __init__(self):
        self.db = DatabaseConfig()
        self.jwt = JWTConfig()
        self.rabbitmq = RabbitMQConfig()