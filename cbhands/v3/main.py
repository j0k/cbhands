"""Main entry point for cbhands v3.0.0."""

import click
import sys
from typing import Optional

from ..core import (
    PluginLoader, PluginRegistry, CommandExecutor, CLIBuilder,
    EventBus, PluginConfigManager, RichFormatter
)
from ..core.commands.middleware import LoggingMiddleware, ValidationMiddleware, TimingMiddleware
from ..core.config import Config


def create_app(config_file: Optional[str] = None) -> click.Group:
    """Create cbhands application."""
    # Initialize core components
    event_bus = EventBus()
    config_manager = PluginConfigManager()
    plugin_registry = PluginRegistry(event_bus)
    command_executor = CommandExecutor(event_bus)
    formatter = RichFormatter()
    
    # Add middleware
    command_executor.middleware_manager.add_middleware(ValidationMiddleware(), "validation")
    command_executor.middleware_manager.add_middleware(TimingMiddleware(), "timing")
    
    # Initialize plugin loader
    plugin_loader = PluginLoader(config_manager, event_bus)
    
    # Load plugins
    plugin_loader.load_plugins_from_entry_points()
    
    # Load built-in plugins
    from ..plugins.service_manager import ServiceManagerPlugin
    from ..plugins.dev_showroom_v3 import DevShowroomV3Plugin
    
    print("Loading service_manager plugin...")
    success = plugin_loader.load_plugin("service_manager", ServiceManagerPlugin)
    print(f"Service manager plugin loaded: {success}")
    
    print("Loading dev_showroom plugin...")
    success = plugin_loader.load_plugin("dev_showroom", DevShowroomV3Plugin)
    print(f"Dev showroom plugin loaded: {success}")
    
    # Register commands from plugins
    for plugin_name in plugin_loader.get_loaded_plugins():
        plugin = plugin_loader.get_plugin(plugin_name)
        if plugin:
            print(f"Registering commands from plugin: {plugin_name}")
            for command_def in plugin.get_commands():
                print(f"  - {command_def.name}")
                command_executor.register_command(command_def)
    
    # Build CLI
    cli_builder = CLIBuilder(plugin_registry, command_executor, formatter, event_bus)
    cli = cli_builder.build_cli()
    
    return cli


def main():
    """Main entry point."""
    try:
        cli = create_app()
        cli()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
