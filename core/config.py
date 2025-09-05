import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    openai_org_id: Optional[str] = Field(None, env="OPENAI_ORG_ID")
    gemini_api_key: Optional[str] = Field(None, env="GEMINI_API_KEY")
    
    debug: bool = Field(False, env="DEBUG")
    log_level: str = Field("info", env="LOG_LEVEL")
    
    data_dir: Path = Field(Path("data"), description="Base directory for all data storage")
    authors_dir: Path = Field(Path("data/authors"), description="Directory for author profiles")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Only create directories if not in test mode
        if not kwargs.get('_skip_directory_creation', False):
            self.ensure_directories()
    
    def ensure_directories(self):
        self.data_dir.mkdir(exist_ok=True)
        self.authors_dir.mkdir(exist_ok=True)
    
    def has_openai_key(self) -> bool:
        return bool(self.openai_api_key)
    
    def has_gemini_key(self) -> bool:
        return bool(self.gemini_api_key)
    
    def validate_provider_access(self, provider: str) -> bool:
        if provider == "openai":
            return self.has_openai_key()
        elif provider == "gemini":
            return self.has_gemini_key()
        return False


settings = Settings()