"""Command definitions for cbhands v3.0.0."""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union, Type
from enum import Enum


class OptionType(Enum):
    """Supported option types."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    CHOICE = "choice"
    MULTIPLE = "multiple"
    FLAG = "flag"


@dataclass
class OptionDefinition:
    """Definition of a command option."""
    name: str
    type: OptionType
    description: str
    default: Any = None
    required: bool = False
    choices: Optional[List[str]] = None
    multiple: bool = False
    help: Optional[str] = None
    short_name: Optional[str] = None
    hidden: bool = False
    envvar: Optional[str] = None
    metavar: Optional[str] = None
    validator: Optional[Callable[[Any], bool]] = None


@dataclass
class CommandGroup:
    """Definition of a command group."""
    name: str
    description: str
    commands: List['CommandDefinition'] = field(default_factory=list)
    hidden: bool = False


@dataclass
class CommandDefinition:
    """Definition of a command."""
    name: str
    description: str
    handler: Callable
    options: List[OptionDefinition] = field(default_factory=list)
    group: Optional[str] = None
    hidden: bool = False
    help: Optional[str] = None
    short_help: Optional[str] = None
    aliases: List[str] = field(default_factory=list)
    deprecated: bool = False
    deprecation_message: Optional[str] = None
    requires_services: List[str] = field(default_factory=list)
    async_handler: Optional[Callable] = None
    middleware: List[str] = field(default_factory=list)


@dataclass
class CommandResult:
    """Result of command execution."""
    success: bool
    message: str
    data: Any = None
    exit_code: int = 0
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    @classmethod
    def success_result(cls, message: str, data: Any = None) -> 'CommandResult':
        """Create a successful result."""
        return cls(success=True, message=message, data=data)
    
    @classmethod
    def error_result(cls, message: str, exit_code: int = 1, errors: List[str] = None) -> 'CommandResult':
        """Create an error result."""
        return cls(
            success=False, 
            message=message, 
            exit_code=exit_code,
            errors=errors or []
        )
    
    @classmethod
    def warning_result(cls, message: str, warnings: List[str], data: Any = None) -> 'CommandResult':
        """Create a result with warnings."""
        return cls(
            success=True, 
            message=message, 
            data=data,
            warnings=warnings
        )
