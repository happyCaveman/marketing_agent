from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = PROJECT_ROOT / ".env"

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
    
    slack_bot_token : str
    slack_app_token : str
    
    temp_storage_dir : str
        
    naver_browser_profile_dir: str = "data/browser/naver"
    naver_blog_url: str
    
    instagram_access_token : str
    instagram_account_id : str
    
    threads_access_token : str
    threads_user_id : str
    
    facebook_page_id : str
    facebook_page_access_token : str
    
    supabase_url : str
    supabase_service_role_key : str
    supabase_storage_bucket : str
    
    model_config = SettingsConfigDict(
        
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
      

settings = Settings()