"""Configuration management for cbhands v3.0.0."""

import os
import yaml
from typing import Any, Dict, Optional
from pathlib import Path


class Config:
    """Main configuration class."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration."""
        self.config_file = config_file or self._get_default_config_file()
        self._config: Dict[str, Any] = {}
        self._load_config()
    
    def _get_default_config_file(self) -> str:
        """Get default configuration file path."""
        config_dir = os.path.expanduser("~/.config/cbhands")
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, "config.yaml")
    
    def _load_config(self) -> None:
        """Load configuration from file."""
        if not os.path.exists(self.config_file):
            self._config = self._get_default_config()
            self._save_config()
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Error loading config: {e}")
            self._config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'services': {
                'lobby': {
                    'port': 6001,
                    'host': 'localhost',
                    'command': 'go run ./cmd/lobby/main.go',
                    'working_dir': '/home/jk/battles/lobby',
                    'env': {
                        'BYPASS_JWT': '1'
                    }
                },
                'dealer': {
                    'port': 6000,
                    'host': 'localhost',
                    'command': 'go run ./cmd/dealer/main.go',
                    'working_dir': '/home/jk/battles/dealer'
                },
                'frontend': {
                    'port': 3000,
                    'host': 'localhost',
                    'command': 'npm run serve',
                    'working_dir': '/home/jk/battles/battle_hands_ts'
                },
                'monitor': {
                    'port': 9001,
                    'host': 'localhost',
                    'command': 'node dist/index.js --port 9001',
                    'working_dir': '/home/jk/battles/cbhands_monitor_ts',
                    'env': {
                        'MONITOR_PORT': '9001'
                    }
                }
            },
            'plugins': {
                'auto_load': True,
                'directories': [],
                'entry_points': 'cbhands.plugins'
            },
            'logging': {
                'level': 'INFO',
                'file': None,
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        }
    
    def _save_config(self) -> None:
        """Save configuration to file."""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self._config, f, default_flow_style=False, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self._save_config()
    
    def get_services(self) -> Dict[str, Any]:
        """Get services configuration."""
        return self.get('services', {})
    
    def get_service_config(self, service_name: str) -> Dict[str, Any]:
        """Get specific service configuration."""
        return self.get(f'services.{service_name}', {})
    
    def get_plugins_config(self) -> Dict[str, Any]:
        """Get plugins configuration."""
        return self.get('plugins', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return self.get('logging', {})
