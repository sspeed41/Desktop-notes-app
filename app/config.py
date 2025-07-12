"""
Configuration management for WiseDesktopNoteApp
Centralized configuration with validation and environment handling
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv


class DatabaseConfig(BaseModel):
    """Database configuration"""
    url: str = Field(..., description="Supabase URL")
    anon_key: str = Field(..., description="Supabase anonymous key")
    service_role: Optional[str] = Field(None, description="Supabase service role key")
    
    @validator('url')
    def validate_url(cls, v):
        # Allow empty URL for development/offline mode
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError('Database URL must start with http:// or https://')
        return v


class UIConfig(BaseModel):
    """UI configuration"""
    colors: Dict[str, str] = Field(default_factory=lambda: {
        "primary": "#1DA1F2",
        "secondary": "#657786",
        "background": "#FFFFFF",
        "surface": "#F7F9FA",
        "text_primary": "#14171A",
        "text_secondary": "#657786",
        "border": "#E1E8ED",
        "hover": "#F7F9FA",
        "success": "#17BF63",
        "warning": "#FFAD1F",
        "error": "#E0245E",
    })
    
    fonts: Dict[str, str] = Field(default_factory=lambda: {
        "primary": "Arial",
        "secondary": "Arial", 
        "mono": "Monaco",
    })


class CacheConfig(BaseModel):
    """Cache configuration"""
    cache_dir: Path = Field(default_factory=lambda: Path.home() / ".wise_desktop_note_app" / "cache")
    size_limit: int = Field(default=1000, description="Maximum number of cached notes")
    max_age_hours: int = Field(default=24, description="Cache expiry time in hours")


class AppConfig(BaseModel):
    """Main application configuration"""
    name: str = Field(default="Racing Notes")
    version: str = Field(default="2.6.0")
    organization: str = Field(default="RacingNotes")
    org_id: str = Field(default="default-org")
    
    # Nested configurations
    database: DatabaseConfig
    ui: UIConfig = Field(default_factory=UIConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    
    # Logging configuration
    log_level: str = Field(default="INFO")
    log_file: Optional[Path] = Field(default=None)
    
    class Config:
        env_nested_delimiter = '__'


class ConfigManager:
    """Configuration manager singleton"""
    
    _instance: Optional['ConfigManager'] = None
    _config: Optional[AppConfig] = None
    
    def __new__(cls) -> 'ConfigManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from environment and files"""
        # Load from .env file
        env_path = Path(__file__).parent.parent / ".env"
        load_dotenv(env_path)
        
        try:
            # Create database config from environment
            database_config = DatabaseConfig(
                url=os.getenv("SUPABASE_URL", ""),
                anon_key=os.getenv("SUPABASE_ANON_KEY", ""),
                service_role=os.getenv("SUPABASE_SERVICE_ROLE")
            )
            
            # Create main config
            self._config = AppConfig(
                database=database_config,
                org_id=os.getenv("ORG_ID", "default-org"),
                log_level=os.getenv("LOG_LEVEL", "INFO").upper()
            )
            
            # Setup logging
            self._setup_logging()
            
            # Log configuration status
            if not database_config.url or not database_config.anon_key:
                logging.warning("Database configuration incomplete - running in offline mode")
            
        except Exception as e:
            # Fallback to minimal config for development
            logging.warning(f"Failed to load full config: {e}")
            self._config = self._create_fallback_config()
            
            # Setup basic logging even with fallback config
            self._setup_logging()
    
    def _create_fallback_config(self) -> AppConfig:
        """Create minimal fallback configuration"""
        return AppConfig(
            database=DatabaseConfig(url="", anon_key="", service_role=None)
        )
    
    def _setup_logging(self) -> None:
        """Setup logging configuration"""
        if not self._config:
            return
            
        log_level = getattr(logging, self._config.log_level, logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Setup console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # Setup root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        root_logger.addHandler(console_handler)
        
        # Setup file handler if specified
        if self._config.log_file:
            self._config.log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(self._config.log_file)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
    
    @property
    def config(self) -> AppConfig:
        """Get current configuration"""
        if self._config is None:
            self.load_config()
        if self._config is None:
            raise RuntimeError("Failed to load configuration")
        return self._config
    
    def reload_config(self) -> None:
        """Reload configuration"""
        self._config = None
        self.load_config()
    
    def is_database_configured(self) -> bool:
        """Check if database is properly configured"""
        return bool(self.config.database.url and self.config.database.anon_key)


# Global configuration instance
config_manager = ConfigManager()

# Convenience accessors
def get_config() -> AppConfig:
    """Get current application configuration"""
    return config_manager.config

def get_database_config() -> DatabaseConfig:
    """Get database configuration"""
    return config_manager.config.database

def get_ui_config() -> UIConfig:
    """Get UI configuration"""
    return config_manager.config.ui

def get_cache_config() -> CacheConfig:
    """Get cache configuration"""
    return config_manager.config.cache 