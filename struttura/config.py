"""Configuration handling for ComicDB."""

import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union

# Default configuration
DEFAULT_CONFIG = {
    'database': {
        'db_type': 'sqlite',
        'database': 'comicdb.sqlite',
        'host': 'localhost',
        'user': '',
        'password': ''
    },
    'language': 'en',
    'check_updates': True,
    'window_geometry': None,
    'recent_files': []
}

def get_config_path() -> Path:
    """Get the path to the config file."""
    config_dir = Path.home() / '.comicdb'
    config_dir.mkdir(exist_ok=True)
    return config_dir / 'config.json'

def get_database_path() -> Path:
    """Get the path to the database file."""
    config = load_config()
    db_path = Path(config['database']['database'])
    
    # If it's a relative path, make it relative to the config directory
    if not db_path.is_absolute():
        return get_config_path().parent / db_path
    return db_path

def load_config() -> Dict[str, Any]:
    """Load the configuration from file."""
    config_path = get_config_path()
    
    # If config file doesn't exist, create it with defaults
    if not config_path.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        # Ensure all default keys exist
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value
                
        return config
    except Exception as e:
        logging.error(f"Error loading config: {e}")
        return DEFAULT_CONFIG.copy()

def save_config(config: Dict[str, Any]) -> None:
    """Save the configuration to file."""
    config_path = get_config_path()
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Error saving config: {e}")

def get_config_value(key: str, default: Any = None) -> Any:
    """Get a configuration value by key."""
    config = load_config()
    return config.get(key, default)

def set_config_value(key: str, value: Any) -> None:
    """Set a configuration value and save it."""
    config = load_config()
    config[key] = value
    save_config(config)

def get_db_config() -> Dict[str, str]:
    """Get the database configuration."""
    config = load_config()
    return config.get('database', {}).copy()
