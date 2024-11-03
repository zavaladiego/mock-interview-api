from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    AWS_AK: str
    AWS_SAK: str
    OPENAI_API_KEY: str

    class Config:
        env_file = '.env'
