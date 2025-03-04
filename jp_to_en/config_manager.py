"""
Configuration manager module for jp-to-en.

This module handles loading and saving configuration, including API keys.
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manager for loading and saving configuration."""
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_dir: Custom configuration directory path (optional)
        """
        # Set up configuration directory
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            # Default to ~/.jp-to-en
            self.config_dir = Path.home() / ".jp-to-en"
            
        # Create config directory if it doesn't exist
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
        # Default config file paths
        self.config_file = self.config_dir / "config.json"
        self.credentials_file = self.config_dir / "credentials.json"
        
        # Default configuration
        self._config = self._load_default_config()
        self._credentials = {}
        
        # Load existing configuration if available
        self._load_config()
        self._load_credentials()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """
        Load default configuration.
        
        Returns:
            Default configuration dictionary
        """
        # Try to load from package config directory
        default_config_path = Path(__file__).parent.parent / "config" / "default.json"
        
        if default_config_path.exists():
            try:
                with open(default_config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load default config: {e}")
                
        # Fallback to minimal default config
        return {
            "translator": {
                "model": "text-translation-3",
                "max_retries": 3,
                "retry_delay": 1.0
            },
            "detector": {
                "min_confidence": 0.5,
                "context_size": 50
            }
        }
    
    def _load_config(self) -> None:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    
                # Merge with default config (user config takes precedence)
                self._deep_update(self._config, user_config)
                    
            except Exception as e:
                logger.warning(f"Failed to load config file: {e}")
    
    def _load_credentials(self) -> None:
        """Load credentials from file."""
        if self.credentials_file.exists():
            try:
                with open(self.credentials_file, 'r', encoding='utf-8') as f:
                    self._credentials = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load credentials file: {e}")
    
    def _deep_update(self, d: Dict[str, Any], u: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively update a dictionary.
        
        Args:
            d: Dictionary to update
            u: Dictionary with updates
            
        Returns:
            Updated dictionary
        """
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                self._deep_update(d[k], v)
            else:
                d[k] = v
        return d
    
    def save_config(self) -> bool:
        """
        Save configuration to file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save config file: {e}")
            return False
    
    def save_credentials(self) -> bool:
        """
        Save credentials to file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.credentials_file, 'w', encoding='utf-8') as f:
                json.dump(self._credentials, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save credentials file: {e}")
            return False
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get the current configuration.
        
        Returns:
            Configuration dictionary
        """
        return self._config
    
    def set_config_value(self, key_path: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key_path: Dot-separated path to the configuration key
            value: Value to set
        """
        keys = key_path.split('.')
        config = self._config
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
            
        # Set the value
        config[keys[-1]] = value
    
    def get_config_value(self, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key_path: Dot-separated path to the configuration key
            default: Default value to return if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        config = self._config
        
        # Navigate to the target key
        for key in keys:
            if not isinstance(config, dict) or key not in config:
                return default
            config = config[key]
            
        return config
    
    def set_api_key(self, api_key: str) -> bool:
        """
        Set and save the OpenAI API key.
        
        Args:
            api_key: OpenAI API key
            
        Returns:
            True if successful, False otherwise
        """
        self._credentials["openai_api_key"] = api_key
        return self.save_credentials()
    
    def get_api_key(self) -> Optional[str]:
        """
        Get the OpenAI API key.
        
        Returns:
            API key if available, None otherwise
        """
        return self._credentials.get("openai_api_key")
