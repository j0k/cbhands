"""Command executor for cbhands v3.0.0."""

from typing import Any, Dict, List, Optional
from .definition import CommandDefinition, CommandResult
from .middleware import MiddlewareManager
from ..plugin.events import EventBus


class CommandExecutor:
    """Executes commands with middleware support."""
    
    def __init__(self, event_bus: Optional[EventBus] = None):
        """Initialize command executor."""
        self.event_bus = event_bus or EventBus()
        self.middleware_manager = MiddlewareManager()
        self._command_cache: Dict[str, CommandDefinition] = {}
    
    def register_command(self, command: CommandDefinition) -> None:
        """Register a command."""
        self._command_cache[command.name] = command
        
        # Emit command registered event
        self.event_bus.emit('command.registered', {
            'command': command.name,
            'group': command.group,
            'description': command.description
        })
    
    def execute(self, command_name: str, ctx: Any, **kwargs) -> CommandResult:
        """Execute a command."""
        command = self._command_cache.get(command_name)
        if not command:
            return CommandResult.error_result(f"Command '{command_name}' not found")
        
        # Emit command execution started event
        self.event_bus.emit('command.execution.started', {
            'command': command_name,
            'args': kwargs
        })
        
        try:
            # Apply middleware
            result = self.middleware_manager.execute(
                command=command,
                ctx=ctx,
                **kwargs
            )
            
            # Emit command execution completed event
            self.event_bus.emit('command.execution.completed', {
                'command': command_name,
                'success': result.success,
                'exit_code': result.exit_code
            })
            
            return result
            
        except Exception as e:
            error_result = CommandResult.error_result(f"Command execution failed: {str(e)}")
            
            # Emit command execution failed event
            self.event_bus.emit('command.execution.failed', {
                'command': command_name,
                'error': str(e)
            })
            
            return error_result
    
    def get_command(self, command_name: str) -> Optional[CommandDefinition]:
        """Get command definition."""
        return self._command_cache.get(command_name)
    
    def list_commands(self) -> List[CommandDefinition]:
        """List all registered commands."""
        return list(self._command_cache.values())
    
    def get_commands_by_group(self, group: str) -> List[CommandDefinition]:
        """Get commands by group."""
        return [cmd for cmd in self._command_cache.values() if cmd.group == group]
    
    def search_commands(self, query: str) -> List[CommandDefinition]:
        """Search commands by name or description."""
        query_lower = query.lower()
        return [
            cmd for cmd in self._command_cache.values()
            if (query_lower in cmd.name.lower() or 
                query_lower in cmd.description.lower())
        ]
    
    def validate_command_args(self, command_name: str, **kwargs) -> List[str]:
        """Validate command arguments."""
        command = self._command_cache.get(command_name)
        if not command:
            return [f"Command '{command_name}' not found"]
        
        errors = []
        
        # Check required options
        for option in command.options:
            if option.required and option.name not in kwargs:
                errors.append(f"Required option '{option.name}' not provided")
        
        # Validate option values
        for option in command.options:
            if option.name in kwargs:
                value = kwargs[option.name]
                if option.validator and not option.validator(value):
                    errors.append(f"Invalid value for option '{option.name}'")
        
        return errors
