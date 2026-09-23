from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    #MongoDB Settings
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "it_servicedesk"
    #Gives the app a name
    APP_NAME: str = "IT Service Desk App API"
    #Informs pydantic-settings to load values from .env file
    model_config = SettingsConfigDict(env_file=".env",env_file_encoding="utf-8")

#shared settings Object that all other files can iport
settings = Settings()