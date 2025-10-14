"""Plugin registry for cbhands v3.0.0."""

from typing import Dict, List, Optional, Set
from .base import BasePlugin
from .events import EventBus


class PluginRegistry:
    """Registry for managing plugins and their commands."""
    
    def __init__(self, event_bus: Optional[EventBus] = None):
        """Initialize plugin registry."""
        self.event_bus = event_bus or EventBus()
        self._plugins: Dict[str, BasePlugin] = {}
        self._commands: Dict[str, str] = {}  # command_name -> plugin_name
        self._groups: Dict[str, Set[str]] = {}  # group_name -> set of plugin_names
        self._dependencies: Dict[str, Set[str]] = {}  # plugin_name -> set of dependencies
    
    def register_plugin(self, plugin: BasePlugin) -> None:
        """Register a plugin."""
        plugin_name = plugin.get_metadata().name
        
        # Check if already registered
        if plugin_name in self._plugins:
            self.unregister_plugin(plugin_name)
        
        # Register plugin
        self._plugins[plugin_name] = plugin
        
        # Register commands
        for command_def in plugin.get_commands():
            self._commands[command_def.name] = plugin_name
            
            # Register group
            if command_def.group:
                if command_def.group not in self._groups:
                    self._groups[command_def.group] = set()
                self._groups[command_def.group].add(plugin_name)
        
        # Register dependencies
        dependencies = plugin.get_dependencies()
        if dependencies:
            self._dependencies[plugin_name] = set(dependencies)
        
        # Emit plugin registered event
        self.event_bus.emit('plugin.registered', {
            'plugin': plugin_name,
            'version': plugin.get_metadata().version,
            'commands': [cmd.name for cmd in plugin.get_commands()]
        })
    
    def unregister_plugin(self, plugin_name: str) -> None:
        """Unregister a plugin."""
        if plugin_name not in self._plugins:
            return
        
        plugin = self._plugins[plugin_name]
        
        # Unregister commands
        commands_to_remove = [
            cmd_name for cmd_name, p_name in self._commands.items()
            if p_name == plugin_name
        ]
        for cmd_name in commands_to_remove:
            del self._commands[cmd_name]
        
        # Unregister from groups
        for group_name, plugins in self._groups.items():
            plugins.discard(plugin_name)
            if not plugins:
                del self._groups[group_name]
        
        # Remove dependencies
        if plugin_name in self._dependencies:
            del self._dependencies[plugin_name]
        
        # Remove plugin
        del self._plugins[plugin_name]
        
        # Emit plugin unregistered event
        self.event_bus.emit('plugin.unregistered', {
            'plugin': plugin_name
        })
    
    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """Get plugin by name."""
        return self._plugins.get(plugin_name)
    
    def get_plugin_for_command(self, command_name: str) -> Optional[BasePlugin]:
        """Get plugin that owns a command."""
        plugin_name = self._commands.get(command_name)
        if plugin_name:
            return self._plugins.get(plugin_name)
        return None
    
    def list_plugins(self) -> List[str]:
        """List all registered plugin names."""
        return list(self._plugins.keys())
    
    def list_commands(self) -> List[str]:
        """List all registered command names."""
        return list(self._commands.keys())
    
    def list_commands_by_plugin(self, plugin_name: str) -> List[str]:
        """List commands owned by a plugin."""
        return [
            cmd_name for cmd_name, p_name in self._commands.items()
            if p_name == plugin_name
        ]
    
    def list_commands_by_group(self, group_name: str) -> List[str]:
        """List commands in a group."""
        if group_name not in self._groups:
            return []
        
        commands = []
        for plugin_name in self._groups[group_name]:
            plugin_commands = self.list_commands_by_plugin(plugin_name)
            commands.extend(plugin_commands)
        return commands
    
    def list_groups(self) -> List[str]:
        """List all command groups."""
        return list(self._groups.keys())
    
    def get_plugin_metadata(self, plugin_name: str) -> Optional[dict]:
        """Get plugin metadata."""
        plugin = self._plugins.get(plugin_name)
        if plugin:
            metadata = plugin.get_metadata()
            return {
                'name': metadata.name,
                'version': metadata.version,
                'description': metadata.description,
                'author': metadata.author,
                'email': metadata.email,
                'url': metadata.url,
                'license': metadata.license,
                'dependencies': metadata.dependencies or [],
                'python_requires': metadata.python_requires
            }
        return None
    
    def get_plugin_dependencies(self, plugin_name: str) -> Set[str]:
        """Get plugin dependencies."""
        return self._dependencies.get(plugin_name, set())
    
    def check_dependency_cycle(self) -> List[List[str]]:
        """Check for circular dependencies."""
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(plugin_name: str, path: List[str]) -> None:
            if plugin_name in rec_stack:
                # Found a cycle
                cycle_start = path.index(plugin_name)
                cycles.append(path[cycle_start:] + [plugin_name])
                return
            
            if plugin_name in visited:
                return
            
            visited.add(plugin_name)
            rec_stack.add(plugin_name)
            
            for dep in self._dependencies.get(plugin_name, set()):
                if dep in self._plugins:  # Only check loaded plugins
                    dfs(dep, path + [plugin_name])
            
            rec_stack.remove(plugin_name)
        
        for plugin_name in self._plugins:
            if plugin_name not in visited:
                dfs(plugin_name, [])
        
        return cycles
    
    def get_plugin_load_order(self) -> List[str]:
        """Get recommended plugin load order based on dependencies."""
        # Simple topological sort
        in_degree = {plugin: 0 for plugin in self._plugins}
        
        # Calculate in-degrees
        for plugin_name in self._plugins:
            for dep in self._dependencies.get(plugin_name, set()):
                if dep in self._plugins:
                    in_degree[plugin_name] += 1
        
        # Find plugins with no dependencies
        queue = [plugin for plugin, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            plugin = queue.pop(0)
            result.append(plugin)
            
            # Update in-degrees of dependent plugins
            for other_plugin in self._plugins:
                if plugin in self._dependencies.get(other_plugin, set()):
                    in_degree[other_plugin] -= 1
                    if in_degree[other_plugin] == 0:
                        queue.append(other_plugin)
        
        return result
    
    def clear(self) -> None:
        """Clear all registered plugins."""
        plugin_names = list(self._plugins.keys())
        for plugin_name in plugin_names:
            self.unregister_plugin(plugin_name)
