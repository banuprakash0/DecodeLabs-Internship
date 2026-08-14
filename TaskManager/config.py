"""Centralized Configuration Module for TaskManager System.

Defines directory paths, file paths, default application settings,
UI color themes, auto-backup settings, and authentication flags.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any

# Base Directories
BASE_DIR: Path = Path(__file__).resolve().parent
DATA_DIR: Path = BASE_DIR / "data"
DOCS_DIR: Path = BASE_DIR / "docs"
LOGS_DIR: Path = DATA_DIR / "logs"

# File Paths
TASKS_FILE: Path = DATA_DIR / "tasks.json"
BACKUP_FILE: Path = DATA_DIR / "tasks_backup.json"
ACTIVITY_LOG_FILE: Path = LOGS_DIR / "activity.log"
AUTH_FILE: Path = DATA_DIR / "auth.json"
SAMPLE_CSV_FILE: Path = DATA_DIR / "sample_tasks.csv"


@dataclass
class AppConfig:
    """Application Configuration Settings."""

    app_name: str = "Enterprise Task Manager"
    version: str = "1.0.0"
    author: str = "Senior Backend Engineering Team"
    
    # Auto-save & Backup settings
    auto_save: bool = True
    auto_backup: bool = True
    max_backups: int = 5
    
    # Security settings
    auth_enabled: bool = False
    session_timeout_minutes: int = 15
    min_password_length: int = 6
    
    # UI Theme Settings
    theme: str = "dark"
    date_format: str = "%Y-%m-%d"
    datetime_format: str = "%Y-%m-%d %H:%M:%S"
    
    # Task Constraints
    max_title_length: int = 100
    max_description_length: int = 500
    
    def ensure_directories(self) -> None:
        """Ensure all required data and log directories exist."""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        DOCS_DIR.mkdir(parents=True, exist_ok=True)
        LOGS_DIR.mkdir(parents=True, exist_ok=True)


# Global Config Singleton
config = AppConfig()
config.ensure_directories()
