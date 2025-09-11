"""Configuration management for cbhands."""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """Configuration manager for cbhands."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration.
        
        Args:
            config_path: Path to configuration file. If None, uses default.
        """
        if config_path is None:
            # Try to find config in several locations
            possible_paths = [
                "config/default.yaml",
                "/etc/cbhands/default.yaml",
                os.path.expanduser("~/.config/cbhands/default.yaml"),
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    config_path = path
                    break
            else:
                raise FileNotFoundError("No configuration file found")
        
        self.config_path = config_path
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to load configuration from {self.config_path}: {e}")
    
    def get_services(self) -> Dict[str, Dict[str, Any]]:
        """Get all services configuration."""
        return self._config.get('services', {})
    
    def get_service(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get specific service configuration."""
        return self.get_services().get(service_name)
    
    def get_settings(self) -> Dict[str, Any]:
        """Get global settings."""
        return self._config.get('settings', {})
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get specific setting value."""
        return self.get_settings().get(key, default)
    
    def reload(self):
        """Reload configuration from file."""
        self._config = self._load_config()
    
    def get_state_file_path(self) -> str:
        """Get path to state file."""
        return self.get_setting('state_file', '/tmp/cbhands_state.yaml')
    
    def get_log_dir(self) -> str:
        """Get log directory path."""
        return self.get_setting('log_dir', '/tmp/cbhands_logs')
    
    def get_pid_dir(self) -> str:
        """Get PID directory path."""
        return self.get_setting('pid_dir', '/tmp/cbhands_pids')
    
    def get_timeout(self) -> int:
        """Get operation timeout in seconds."""
        return self.get_setting('timeout', 30)
