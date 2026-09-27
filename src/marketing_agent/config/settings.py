from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "development"
    log_level: str = "INFO"
    
    llm_provider: str = "claude"
    claude_api_key: str | None = None
    
    vector_db_url: str | None = None
    vector_db_api_key: str | None = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    

settings = Settings()