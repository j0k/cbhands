"""Plugin loader for cbhands v3.0.0."""

import importlib
import pkg_resources
from typing import Dict, List, Optional, Type, Any
from pathlib import Path
import sys
import os

from .base import BasePlugin, PluginMetadata
from .registry import PluginRegistry
from .events import EventBus
from ..config.plugin_config import PluginConfig, PluginConfigManager


class PluginLoader:
    """Loads and manages plugins."""
    
    def __init__(self, config_manager: Optional[PluginConfigManager] = None, event_bus: Optional[EventBus] = None):
        """Initialize plugin loader."""
        self.config_manager = config_manager or PluginConfigManager()
        self.event_bus = event_bus or EventBus()
        self.registry = PluginRegistry()
        self._loaded_plugins: Dict[str, BasePlugin] = {}
        self._plugin_modules: Dict[str, Any] = {}
    
    def load_plugin(self, plugin_name: str, plugin_class: Type[BasePlugin], config: Optional[PluginConfig] = None) -> bool:
        """Load a plugin by class."""
        try:
            # Check if plugin is enabled
            plugin_config = config or self.config_manager.get_config(plugin_name)
            if not plugin_config.enabled:
                return False
            
            # Check dependencies
            plugin_instance = plugin_class(plugin_config, self.event_bus)
            missing_deps = plugin_instance.check_dependencies()
            if missing_deps:
                print(f"Plugin {plugin_name} has missing dependencies: {missing_deps}")
                return False
            
            # Initialize plugin
            plugin_instance.initialize()
            
            # Register plugin
            self.registry.register_plugin(plugin_instance)
            self._loaded_plugins[plugin_name] = plugin_instance
            
            # Emit plugin loaded event
            self.event_bus.emit('plugin.loaded', {
                'plugin': plugin_name,
                'version': plugin_instance.get_metadata().version
            })
            
            return True
            
        except Exception as e:
            print(f"Failed to load plugin {plugin_name}: {e}")
            return False
    
    def load_plugin_from_module(self, module_name: str, plugin_name: str) -> bool:
        """Load plugin from module."""
        try:
            # Import module
            module = importlib.import_module(module_name)
            self._plugin_modules[plugin_name] = module
            
            # Find plugin class
            plugin_class = getattr(module, plugin_name, None)
            if not plugin_class or not issubclass(plugin_class, BasePlugin):
                print(f"No valid plugin class found in {module_name}")
                return False
            
            return self.load_plugin(plugin_name, plugin_class)
            
        except Exception as e:
            print(f"Failed to load plugin from module {module_name}: {e}")
            return False
    
    def load_plugins_from_entry_points(self, entry_point_group: str = 'cbhands.plugins') -> List[str]:
        """Load plugins from entry points."""
        loaded = []
        
        try:
            for entry_point in pkg_resources.iter_entry_points(entry_point_group):
                try:
                    plugin_class = entry_point.load()
                    if self.load_plugin(entry_point.name, plugin_class):
                        loaded.append(entry_point.name)
                except Exception as e:
                    print(f"Failed to load plugin {entry_point.name}: {e}")
        except Exception as e:
            print(f"Failed to load plugins from entry points: {e}")
        
        return loaded
    
    def load_plugins_from_directory(self, directory: str) -> List[str]:
        """Load plugins from directory."""
        loaded = []
        plugin_dir = Path(directory)
        
        if not plugin_dir.exists():
            return loaded
        
        # Add directory to Python path
        if str(plugin_dir) not in sys.path:
            sys.path.insert(0, str(plugin_dir))
        
        # Find Python files
        for py_file in plugin_dir.glob("*.py"):
            if py_file.name.startswith("__"):
                continue
            
            module_name = py_file.stem
            try:
                module = importlib.import_module(module_name)
                
                # Look for plugin classes
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, BasePlugin) and 
                        attr != BasePlugin):
                        
                        plugin_name = getattr(attr, 'name', attr_name)
                        if self.load_plugin(plugin_name, attr):
                            loaded.append(plugin_name)
                            
            except Exception as e:
                print(f"Failed to load plugin from {py_file}: {e}")
        
        return loaded
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin."""
        if plugin_name not in self._loaded_plugins:
            return False
        
        try:
            plugin = self._loaded_plugins[plugin_name]
            plugin.cleanup()
            
            # Unregister from registry
            self.registry.unregister_plugin(plugin_name)
            
            # Remove from loaded plugins
            del self._loaded_plugins[plugin_name]
            
            # Emit plugin unloaded event
            self.event_bus.emit('plugin.unloaded', {
                'plugin': plugin_name
            })
            
            return True
            
        except Exception as e:
            print(f"Failed to unload plugin {plugin_name}: {e}")
            return False
    
    def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a plugin."""
        if plugin_name not in self._loaded_plugins:
            return False
        
        # Unload first
        if not self.unload_plugin(plugin_name):
            return False
        
        # Reload module if it was loaded from module
        if plugin_name in self._plugin_modules:
            module = self._plugin_modules[plugin_name]
            importlib.reload(module)
        
        # Load again
        return self.load_plugin(plugin_name, self._loaded_plugins[plugin_name].__class__)
    
    def get_loaded_plugins(self) -> List[str]:
        """Get list of loaded plugin names."""
        return list(self._loaded_plugins.keys())
    
    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """Get loaded plugin."""
        return self._loaded_plugins.get(plugin_name)
    
    def is_plugin_loaded(self, plugin_name: str) -> bool:
        """Check if plugin is loaded."""
        return plugin_name in self._loaded_plugins
    
    def shutdown(self) -> None:
        """Shutdown plugin loader."""
        # Unload all plugins
        for plugin_name in list(self._loaded_plugins.keys()):
            self.unload_plugin(plugin_name)
        
        # Clear registry
        self.registry.clear()
        
        # Emit shutdown event
        self.event_bus.emit('plugin.loader.shutdown', {})
