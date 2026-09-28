from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "development"
    log_level: str = "INFO"
    
    llm_provider: str | None = None
    gemini_api_key: str | None = None
    gemini_model : str | None = None
    gemini_embedding_model: str 
    
    google_service_account_file: str
    google_spreadsheet_id: str
    google_prompt_sheet_name: str = "prompts"
    
    google_drive_folder_id: str
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "learning_knowledge"
    
    vector_db_url: str | None = None
    vector_db_api_key: str | None = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    

settings = Settings()