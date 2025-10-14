"""Legacy compatibility layer for cbhands v3.0.0."""

import warnings
from typing import Dict, Any, Optional
from .core import BasePlugin, CommandDefinition, OptionDefinition, OptionType, CommandResult
from .core.config import PluginConfig


class LegacyPluginAdapter(BasePlugin):
    """Adapter for legacy plugins to work with v3.0.0."""
    
    def __init__(self, legacy_plugin, config: Optional[PluginConfig] = None, event_bus=None):
        """Initialize adapter with legacy plugin."""
        super().__init__(config, event_bus)
        self.legacy_plugin = legacy_plugin
        self._warned_about_deprecation = False
    
    def get_metadata(self):
        """Get metadata from legacy plugin."""
        from .core.plugin.base import PluginMetadata
        
        return PluginMetadata(
            name=getattr(self.legacy_plugin, 'name', 'unknown'),
            version=getattr(self.legacy_plugin, 'version', '1.0.0'),
            description=getattr(self.legacy_plugin, 'description', 'Legacy plugin'),
            author=getattr(self.legacy_plugin, 'author', None),
            email=getattr(self.legacy_plugin, 'email', None),
            url=getattr(self.legacy_plugin, 'url', None),
            license=getattr(self.legacy_plugin, 'license', None)
        )
    
    def get_commands(self):
        """Convert legacy commands to v3.0.0 format."""
        if not self._warned_about_deprecation:
            warnings.warn(
                f"Plugin {self.get_metadata().name} uses legacy API. "
                "Please update to v3.0.0 plugin format.",
                DeprecationWarning,
                stacklevel=2
            )
            self._warned_about_deprecation = True
        
        commands = []
        
        # Get legacy commands
        if hasattr(self.legacy_plugin, 'get_commands'):
            legacy_commands = self.legacy_plugin.get_commands()
            
            for cmd_name, cmd_func in legacy_commands.items():
                # Create command definition
                cmd_def = CommandDefinition(
                    name=cmd_name,
                    description=getattr(cmd_func, '__doc__', f"Legacy command: {cmd_name}"),
                    handler=self._create_legacy_handler(cmd_func),
                    group=getattr(self.legacy_plugin, 'name', 'legacy')
                )
                commands.append(cmd_def)
        
        return commands
    
    def _create_legacy_handler(self, legacy_func):
        """Create handler for legacy command function."""
        def handler(ctx, **kwargs):
            """Legacy command handler."""
            try:
                # Call legacy function
                result = legacy_func(**kwargs)
                
                # Convert result to CommandResult
                if isinstance(result, CommandResult):
                    return result
                elif isinstance(result, tuple) and len(result) == 2:
                    success, message = result
                    return CommandResult.success_result(message) if success else CommandResult.error_result(message)
                elif isinstance(result, str):
                    return CommandResult.success_result(result)
                else:
                    return CommandResult.success_result(str(result), result)
                    
            except Exception as e:
                return CommandResult.error_result(f"Legacy command failed: {str(e)}")
        
        return handler


def migrate_legacy_plugin(legacy_plugin) -> LegacyPluginAdapter:
    """Migrate legacy plugin to v3.0.0 format."""
    return LegacyPluginAdapter(legacy_plugin)


def create_legacy_compatibility_layer():
    """Create compatibility layer for legacy plugins."""
    # This function can be used to set up compatibility for old plugins
    pass
