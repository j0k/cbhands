"""Middleware system for cbhands v3.0.0."""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional
from .definition import CommandDefinition, CommandResult


class Middleware(ABC):
    """Base class for middleware."""
    
    @abstractmethod
    def before_execution(self, command: CommandDefinition, ctx: Any, **kwargs) -> Optional[CommandResult]:
        """Called before command execution. Return CommandResult to short-circuit execution."""
        pass
    
    @abstractmethod
    def after_execution(self, command: CommandDefinition, ctx: Any, result: CommandResult, **kwargs) -> CommandResult:
        """Called after command execution. Can modify the result."""
        pass
    
    def on_error(self, command: CommandDefinition, ctx: Any, error: Exception, **kwargs) -> CommandResult:
        """Called when command execution fails."""
        return CommandResult.error_result(f"Command failed: {str(error)}")


class MiddlewareManager:
    """Manages middleware execution."""
    
    def __init__(self):
        """Initialize middleware manager."""
        self._middleware: List[Middleware] = []
        self._named_middleware: Dict[str, Middleware] = {}
    
    def add_middleware(self, middleware: Middleware, name: Optional[str] = None) -> None:
        """Add middleware."""
        self._middleware.append(middleware)
        if name:
            self._named_middleware[name] = middleware
    
    def remove_middleware(self, middleware: Middleware) -> None:
        """Remove middleware."""
        if middleware in self._middleware:
            self._middleware.remove(middleware)
    
    def remove_middleware_by_name(self, name: str) -> None:
        """Remove middleware by name."""
        if name in self._named_middleware:
            middleware = self._named_middleware[name]
            self.remove_middleware(middleware)
            del self._named_middleware[name]
    
    def execute(self, command: CommandDefinition, ctx: Any, **kwargs) -> CommandResult:
        """Execute command with middleware."""
        # Execute before middleware
        for middleware in self._middleware:
            result = middleware.before_execution(command, ctx, **kwargs)
            if result is not None:
                return result
        
        # Execute command
        try:
            result = command.handler(ctx, **kwargs)
            if not isinstance(result, CommandResult):
                result = CommandResult.success_result(str(result), result)
        except Exception as e:
            # Execute error middleware
            for middleware in self._middleware:
                result = middleware.on_error(command, ctx, e, **kwargs)
                if result is not None:
                    break
            else:
                result = CommandResult.error_result(f"Command failed: {str(e)}")
        
        # Execute after middleware
        for middleware in reversed(self._middleware):
            result = middleware.after_execution(command, ctx, result, **kwargs)
        
        return result


class LoggingMiddleware(Middleware):
    """Middleware for logging command execution."""
    
    def __init__(self, logger):
        """Initialize logging middleware."""
        self.logger = logger
    
    def before_execution(self, command: CommandDefinition, ctx: Any, **kwargs) -> Optional[CommandResult]:
        """Log command start."""
        self.logger.info(f"Executing command: {command.name}")
        return None
    
    def after_execution(self, command: CommandDefinition, ctx: Any, result: CommandResult, **kwargs) -> CommandResult:
        """Log command completion."""
        if result.success:
            self.logger.info(f"Command {command.name} completed successfully")
        else:
            self.logger.error(f"Command {command.name} failed: {result.message}")
        return result


class ValidationMiddleware(Middleware):
    """Middleware for command validation."""
    
    def before_execution(self, command: CommandDefinition, ctx: Any, **kwargs) -> Optional[CommandResult]:
        """Validate command arguments."""
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
        
        if errors:
            return CommandResult.error_result("Validation failed", errors=errors)
        
        return None
    
    def after_execution(self, command: CommandDefinition, ctx: Any, result: CommandResult, **kwargs) -> CommandResult:
        """No post-validation needed."""
        return result


class TimingMiddleware(Middleware):
    """Middleware for timing command execution."""
    
    def __init__(self):
        """Initialize timing middleware."""
        self._start_times: Dict[str, float] = {}
    
    def before_execution(self, command: CommandDefinition, ctx: Any, **kwargs) -> Optional[CommandResult]:
        """Record start time."""
        import time
        self._start_times[command.name] = time.time()
        return None
    
    def after_execution(self, command: CommandDefinition, ctx: Any, result: CommandResult, **kwargs) -> CommandResult:
        """Calculate and add timing information."""
        import time
        if command.name in self._start_times:
            duration = time.time() - self._start_times[command.name]
            result.data = result.data or {}
            if isinstance(result.data, dict):
                result.data['execution_time'] = duration
            del self._start_times[command.name]
        return result
