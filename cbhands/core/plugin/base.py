"""Base classes for plugins in cbhands v3.0.0."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Type, Callable
from .events import EventBus
from ..commands.definition import CommandDefinition, CommandResult
from ..config.plugin_config import PluginConfig


@dataclass
class PluginMetadata:
    """Metadata for a plugin."""
    name: str
    version: str
    description: str
    author: Optional[str] = None
    email: Optional[str] = None
    url: Optional[str] = None
    license: Optional[str] = None
    dependencies: List[str] = None
    python_requires: Optional[str] = None
    entry_points: Dict[str, str] = None


class BaseCommand(ABC):
    """Base class for plugin commands."""
    
    def __init__(self, plugin: 'BasePlugin'):
        """Initialize command with plugin reference."""
        self.plugin = plugin
        self.event_bus = plugin.event_bus
        self.config = plugin.config
    
    @abstractmethod
    def get_definition(self) -> CommandDefinition:
        """Get command definition."""
        pass
    
    def execute(self, ctx: Any, **kwargs) -> CommandResult:
        """Execute the command."""
        try:
            return self._execute_impl(ctx, **kwargs)
        except Exception as e:
            return CommandResult.error_result(f"Command failed: {str(e)}")
    
    @abstractmethod
    def _execute_impl(self, ctx: Any, **kwargs) -> CommandResult:
        """Implementation of command execution."""
        pass
    
    def validate_options(self, **kwargs) -> List[str]:
        """Validate command options. Return list of errors."""
        return []
    
    def get_help_text(self) -> str:
        """Get help text for the command."""
        return self.get_definition().description


class BasePlugin(ABC):
    """Base class for cbhands plugins."""
    
    def __init__(self, config: Optional[PluginConfig] = None, event_bus: Optional[EventBus] = None):
        """Initialize plugin."""
        self.config = config or PluginConfig(self.get_metadata().name, {})
        self.event_bus = event_bus or EventBus()
        self._commands: List[BaseCommand] = []
        self._initialized = False
    
    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        pass
    
    @abstractmethod
    def get_commands(self) -> List[CommandDefinition]:
        """Get command definitions from this plugin."""
        pass
    
    def initialize(self) -> None:
        """Initialize the plugin."""
        if self._initialized:
            return
        
        self._setup_commands()
        self._on_initialize()
        self._initialized = True
        
        # Emit initialization event
        self.event_bus.emit('plugin.initialized', {
            'plugin': self.get_metadata().name,
            'version': self.get_metadata().version
        })
    
    def cleanup(self) -> None:
        """Cleanup plugin resources."""
        if not self._initialized:
            return
        
        self._on_cleanup()
        self._initialized = False
        
        # Emit cleanup event
        self.event_bus.emit('plugin.cleanup', {
            'plugin': self.get_metadata().name
        })
    
    def _setup_commands(self) -> None:
        """Setup command instances."""
        self._commands = []
        for cmd_def in self.get_commands():
            cmd_instance = self._create_command_instance(cmd_def)
            if cmd_instance:
                self._commands.append(cmd_instance)
    
    def _create_command_instance(self, cmd_def: CommandDefinition) -> Optional[BaseCommand]:
        """Create command instance from definition."""
        # This should be implemented by subclasses
        return None
    
    def _on_initialize(self) -> None:
        """Called during plugin initialization. Override in subclasses."""
        pass
    
    def _on_cleanup(self) -> None:
        """Called during plugin cleanup. Override in subclasses."""
        pass
    
    def get_command_instances(self) -> List[BaseCommand]:
        """Get command instances."""
        return self._commands.copy()
    
    def is_initialized(self) -> bool:
        """Check if plugin is initialized."""
        return self._initialized
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Get configuration schema for this plugin."""
        return {}
    
    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate plugin configuration. Return list of errors."""
        return []
    
    def on_config_change(self, old_config: Dict[str, Any], new_config: Dict[str, Any]) -> None:
        """Called when plugin configuration changes."""
        pass
    
    def get_dependencies(self) -> List[str]:
        """Get plugin dependencies."""
        return self.get_metadata().dependencies or []
    
    def check_dependencies(self) -> List[str]:
        """Check if plugin dependencies are satisfied. Return list of missing dependencies."""
        missing = []
        for dep in self.get_dependencies():
            try:
                __import__(dep)
            except ImportError:
                missing.append(dep)
        return missing
