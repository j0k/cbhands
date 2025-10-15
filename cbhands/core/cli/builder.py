"""CLI builder for cbhands v3.0.0."""

import click
from typing import Any, Dict, List, Optional, Type
from click import Group, Command, Option

from ..plugin.registry import PluginRegistry
from ..commands.definition import CommandDefinition, OptionDefinition, OptionType
from ..commands.executor import CommandExecutor
from ..plugin.events import EventBus
from .formatter import OutputFormatter


class CLIBuilder:
    """Builds Click CLI from plugin commands."""
    
    def __init__(self, 
                 registry: PluginRegistry,
                 executor: CommandExecutor,
                 formatter: Optional[OutputFormatter] = None,
                 event_bus: Optional[EventBus] = None):
        """Initialize CLI builder."""
        self.registry = registry
        self.executor = executor
        self.formatter = formatter or OutputFormatter()
        self.event_bus = event_bus or EventBus()
        self._built_groups: Dict[str, Group] = {}
    
    def build_cli(self, main_group: Optional[Group] = None) -> Group:
        """Build complete CLI from registered plugins."""
        if main_group is None:
            main_group = click.Group(
                name='cbhands',
                help='Battle Hands Service Manager - утилита для управления сервисами игры Battle Hands.'
            )
        
        # Add core commands
        self._add_core_commands(main_group)
        
        # Add plugin commands
        self._add_plugin_commands(main_group)
        
        # Add plugin information to help
        self._add_plugin_help(main_group)
        
        return main_group
    
    def _add_core_commands(self, main_group: Group) -> None:
        """Add core cbhands commands."""
        
        @main_group.command()
        @click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
        def plugins(verbose: bool):
            """List all available plugins."""
            # Get plugins from executor instead of registry
            all_commands = self.executor.list_commands()
            plugin_groups = {}
            
            for cmd_def in all_commands:
                group_name = cmd_def.group or 'default'
                if group_name not in plugin_groups:
                    plugin_groups[group_name] = {
                        'commands': [],
                        'description': f"{group_name} plugin"
                    }
                plugin_groups[group_name]['commands'].append(cmd_def.name)
            
            if not plugin_groups:
                click.echo("No plugins loaded.")
                return
            
            click.echo("Available Plugins:")
            click.echo("=" * 30)
            
            for plugin_name, info in plugin_groups.items():
                click.echo(f"{plugin_name} - {info['description']}")
                if verbose:
                    if info['commands']:
                        click.echo(f"  Commands: {', '.join(info['commands'])}")
                click.echo()
        
        @main_group.command()
        @click.argument('plugin_name')
        def plugin_info(plugin_name: str):
            """Show detailed information about a plugin."""
            metadata = self.registry.get_plugin_metadata(plugin_name)
            if not metadata:
                click.echo(f"Plugin '{plugin_name}' not found.")
                return
            
            click.echo(f"Plugin: {metadata['name']}")
            click.echo(f"Version: {metadata['version']}")
            click.echo(f"Description: {metadata['description']}")
            
            if metadata['author']:
                click.echo(f"Author: {metadata['author']}")
            if metadata['email']:
                click.echo(f"Email: {metadata['email']}")
            if metadata['url']:
                click.echo(f"URL: {metadata['url']}")
            if metadata['license']:
                click.echo(f"License: {metadata['license']}")
            
            commands = self.registry.list_commands_by_plugin(plugin_name)
            if commands:
                click.echo(f"Commands: {', '.join(commands)}")
            
            deps = self.registry.get_plugin_dependencies(plugin_name)
            if deps:
                click.echo(f"Dependencies: {', '.join(deps)}")
        
        @main_group.command()
        def groups():
            """List all command groups."""
            # Get groups from executor instead of registry
            all_commands = self.executor.list_commands()
            groups = {}
            
            for cmd_def in all_commands:
                group_name = cmd_def.group or 'default'
                if group_name not in groups:
                    groups[group_name] = []
                groups[group_name].append(cmd_def.name)
            
            if not groups:
                click.echo("No command groups found.")
                return
            
            click.echo("Command Groups:")
            click.echo("=" * 20)
            
            for group_name, commands in groups.items():
                click.echo(f"{group_name}: {', '.join(commands)}")
    
    def _add_plugin_commands(self, main_group: Group) -> None:
        """Add commands from plugins."""
        # Get commands from executor instead of registry
        all_commands = self.executor.list_commands()
        
        # Group commands by plugin
        plugin_commands: Dict[str, List[CommandDefinition]] = {}
        
        for cmd_def in all_commands:
            plugin_name = cmd_def.group or 'default'
            if plugin_name not in plugin_commands:
                plugin_commands[plugin_name] = []
            plugin_commands[plugin_name].append(cmd_def)
        
        # Create plugin groups
        for plugin_name, commands in plugin_commands.items():
            group_name = plugin_name.replace('_', '-')
            plugin_group = self._create_plugin_group(plugin_name, group_name, commands)
            main_group.add_command(plugin_group)
            self._built_groups[group_name] = plugin_group
    
    def _create_plugin_group(self, plugin_name: str, group_name: str, commands: List[CommandDefinition]) -> Group:
        """Create a Click group for a plugin."""
        plugin = self.registry.get_plugin(plugin_name)
        metadata = plugin.get_metadata() if plugin else None
        
        group = click.Group(
            name=group_name,
            help=metadata.description if metadata else f"Commands from {plugin_name} plugin"
        )
        
        # Add commands to group
        for cmd_def in commands:
            command = self._create_command(cmd_def)
            group.add_command(command)
        
        return group
    
    def _create_command(self, cmd_def: CommandDefinition) -> Command:
        """Create a Click command from definition."""
        def command_handler(**kwargs):
            """Command handler."""
            # Get context
            ctx = click.get_current_context()
            
            # Execute command
            result = self.executor.execute(cmd_def.name, ctx, **kwargs)
            
            # Handle result
            if result.success:
                if result.message:
                    click.echo(self.formatter.format_success(result.message))
                if result.data:
                    click.echo(self.formatter.format_data(result.data))
                if result.warnings:
                    for warning in result.warnings:
                        click.echo(self.formatter.format_warning(warning))
            else:
                if result.message:
                    click.echo(self.formatter.format_error(result.message), err=True)
                if result.errors:
                    for error in result.errors:
                        click.echo(self.formatter.format_error(error), err=True)
                ctx.exit(result.exit_code)
        
        # Create command
        command = Command(
            name=cmd_def.name,
            help=cmd_def.description,
            callback=command_handler
        )
        
        # Add options
        for option_def in cmd_def.options:
            option = self._create_option(option_def)
            command.params.append(option)
        
        return command
    
    def _create_option(self, option_def: OptionDefinition) -> Option:
        """Create a Click option from definition."""
        # Map option types
        type_map = {
            OptionType.STRING: str,
            OptionType.INTEGER: int,
            OptionType.FLOAT: float,
            OptionType.BOOLEAN: bool,
            OptionType.CHOICE: str,
            OptionType.MULTIPLE: str,
            OptionType.FLAG: bool
        }
        
        option_type = type_map.get(option_def.type, str)
        
        # Special handling for flags
        if option_def.type == OptionType.FLAG:
            # For flags, use is_flag=True
            option = Option(
                param_decls=[f"--{option_def.name}"] + ([f"-{option_def.short_name}"] if option_def.short_name else []),
                type=bool,
                default=option_def.default,
                help=option_def.help or option_def.description,
                required=option_def.required,
                multiple=option_def.multiple,
                hidden=option_def.hidden,
                metavar=option_def.metavar,
                envvar=option_def.envvar,
                is_flag=True
            )
        else:
            # Create option
            option = Option(
                param_decls=[f"--{option_def.name}"] + ([f"-{option_def.short_name}"] if option_def.short_name else []),
                type=option_type,
                default=option_def.default,
                help=option_def.help or option_def.description,
                required=option_def.required,
                multiple=option_def.multiple,
                hidden=option_def.hidden,
                metavar=option_def.metavar,
                envvar=option_def.envvar
            )
        
        return option
    
    def _add_plugin_help(self, main_group: Group) -> None:
        """Add plugin information to main group help."""
        # Get plugins from executor instead of registry
        all_commands = self.executor.list_commands()
        plugin_groups = set()
        
        for cmd_def in all_commands:
            if cmd_def.group:
                plugin_groups.add(cmd_def.group)
        
        if not plugin_groups:
            return
        
        # Get plugin info
        plugin_info = []
        for group_name in plugin_groups:
            plugin_info.append(f"{group_name} - Plugin commands")
        
        if plugin_info:
            help_text = main_group.help or ""
            help_text += f"\n\nAvailable Plugins:\n"
            help_text += "=" * 30 + "\n"
            help_text += "\n".join(plugin_info) + "\n"
            main_group.help = help_text
