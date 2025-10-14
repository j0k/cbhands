"""Plugin configuration for cbhands v3.0.0."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
import yaml
import os
from pathlib import Path


@dataclass
class PluginConfig:
    """Configuration for a plugin."""
    name: str
    config: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    priority: int = 0
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self.config[key] = value
    
    def has(self, key: str) -> bool:
        """Check if configuration key exists."""
        return key in self.config
    
    def get_nested(self, key_path: str, default: Any = None) -> Any:
        """Get nested configuration value using dot notation."""
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set_nested(self, key_path: str, value: Any) -> None:
        """Set nested configuration value using dot notation."""
        keys = key_path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
    
    def merge(self, other: 'PluginConfig') -> None:
        """Merge another plugin configuration."""
        self._merge_dict(self.config, other.config)
        if not self.enabled:
            self.enabled = other.enabled
        if self.priority == 0:
            self.priority = other.priority
    
    def _merge_dict(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """Recursively merge dictionaries."""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._merge_dict(target[key], value)
            else:
                target[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'enabled': self.enabled,
            'priority': self.priority,
            'config': self.config
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PluginConfig':
        """Create from dictionary."""
        return cls(
            name=data['name'],
            enabled=data.get('enabled', True),
            priority=data.get('priority', 0),
            config=data.get('config', {})
        )


class PluginConfigManager:
    """Manager for plugin configurations."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration manager."""
        self.config_file = config_file or self._get_default_config_file()
        self._configs: Dict[str, PluginConfig] = {}
        self._load_configs()
    
    def _get_default_config_file(self) -> str:
        """Get default configuration file path."""
        config_dir = os.path.expanduser("~/.config/cbhands")
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, "plugins.yaml")
    
    def _load_configs(self) -> None:
        """Load configurations from file."""
        if not os.path.exists(self.config_file):
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            
            for plugin_name, plugin_data in data.get('plugins', {}).items():
                self._configs[plugin_name] = PluginConfig.from_dict({
                    'name': plugin_name,
                    **plugin_data
                })
        except Exception as e:
            print(f"Error loading plugin configurations: {e}")
    
    def save_configs(self) -> None:
        """Save configurations to file."""
        try:
            data = {
                'plugins': {
                    name: config.to_dict() for name, config in self._configs.items()
                }
            }
            
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, indent=2)
        except Exception as e:
            print(f"Error saving plugin configurations: {e}")
    
    def get_config(self, plugin_name: str) -> PluginConfig:
        """Get configuration for a plugin."""
        return self._configs.get(plugin_name, PluginConfig(name=plugin_name))
    
    def set_config(self, plugin_name: str, config: PluginConfig) -> None:
        """Set configuration for a plugin."""
        self._configs[plugin_name] = config
    
    def update_config(self, plugin_name: str, **kwargs) -> None:
        """Update configuration for a plugin."""
        config = self.get_config(plugin_name)
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        self.set_config(plugin_name, config)
    
    def remove_config(self, plugin_name: str) -> None:
        """Remove configuration for a plugin."""
        if plugin_name in self._configs:
            del self._configs[plugin_name]
    
    def list_configs(self) -> List[str]:
        """List all configured plugins."""
        return list(self._configs.keys())
    
    def is_enabled(self, plugin_name: str) -> bool:
        """Check if plugin is enabled."""
        config = self.get_config(plugin_name)
        return config.enabled
    
    def enable_plugin(self, plugin_name: str) -> None:
        """Enable a plugin."""
        self.update_config(plugin_name, enabled=True)
    
    def disable_plugin(self, plugin_name: str) -> None:
        """Disable a plugin."""
        self.update_config(plugin_name, enabled=False)
