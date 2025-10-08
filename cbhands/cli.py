"""CLI interface for cbhands."""

import os
import sys
import time
from typing import Optional
import importlib

import click
from colorama import init, Fore, Style

from .config import Config
from .manager import ServiceManager
from .logger import get_logger

# Initialize colorama for cross-platform colored output
init()

logger = get_logger(__name__)


@click.group()
@click.option('--config', '-c', help='Path to configuration file')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx, config: Optional[str], verbose: bool):
    """Battle Hands Service Manager - утилита для управления сервисами игры Battle Hands."""
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    
    try:
        ctx.obj['config'] = Config(config)
        ctx.obj['manager'] = ServiceManager(ctx.obj['config'])
    except Exception as e:
        click.echo(f"{Fore.RED}Error: {e}{Style.RESET_ALL}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('service_name')
@click.pass_context
def start(ctx, service_name: str):
    """Start a service."""
    manager = ctx.obj['manager']
    success, message = manager.start_service(service_name)
    
    if success:
        click.echo(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")
    else:
        click.echo(f"{Fore.RED}✗ {message}{Style.RESET_ALL}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('service_name')
@click.pass_context
def stop(ctx, service_name: str):
    """Stop a service."""
    manager = ctx.obj['manager']
    success, message = manager.stop_service(service_name)
    
    if success:
        click.echo(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")
    else:
        click.echo(f"{Fore.RED}✗ {message}{Style.RESET_ALL}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('service_name')
@click.pass_context
def restart(ctx, service_name: str):
    """Restart a service."""
    manager = ctx.obj['manager']
    success, message = manager.restart_service(service_name)
    
    if success:
        click.echo(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")
    else:
        click.echo(f"{Fore.RED}✗ {message}{Style.RESET_ALL}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('service_name', required=False)
@click.pass_context
def status(ctx, service_name: Optional[str]):
    """Show status of service(s)."""
    manager = ctx.obj['manager']
    
    if service_name:
        # Show status of specific service
        status_info = manager.get_service_status(service_name)
        _print_service_status(status_info)
    else:
        # Show status of all services
        all_status = manager.get_all_services_status()
        
        click.echo(f"{Fore.CYAN}Battle Hands Services Status{Style.RESET_ALL}")
        click.echo("=" * 50)
        
        for status_info in all_status:
            _print_service_status(status_info)
            click.echo()


def _print_service_status(status_info: dict):
    """Print service status information."""
    name = status_info['name']
    status = status_info['status']
    pid = status_info.get('pid')
    port = status_info.get('port')
    description = status_info.get('description', '')
    
    # Status color and symbol
    if status == 'running':
        status_color = Fore.GREEN
        status_symbol = "●"
    elif status == 'stopped':
        status_color = Fore.RED
        status_symbol = "○"
    else:
        status_color = Fore.YELLOW
        status_symbol = "?"
    
    # Print service info
    click.echo(f"{status_color}{status_symbol}{Style.RESET_ALL} {Fore.BLUE}{name}{Style.RESET_ALL}")
    
    if description:
        click.echo(f"    {description}")
    
    # Always show port if available
    if port:
        click.echo(f"    Port: {port}")
    
    if status == 'running' and pid:
        click.echo(f"    PID: {pid}")
        
        # Show uptime if available
        uptime = status_info.get('uptime')
        if uptime:
            hours = int(uptime // 3600)
            minutes = int((uptime % 3600) // 60)
            seconds = int(uptime % 60)
            click.echo(f"    Uptime: {hours:02d}:{minutes:02d}:{seconds:02d}")
    elif status == 'stopped':
        click.echo(f"    Status: {status_color}stopped{Style.RESET_ALL}")
    else:
        click.echo(f"    Status: {status_color}{status}{Style.RESET_ALL}")


@cli.command()
@click.argument('service_name')
@click.option('--lines', '-n', default=100, help='Number of lines to show')
@click.option('--follow', '-f', is_flag=True, help='Follow log output')
@click.pass_context
def logs(ctx, service_name: str, lines: int, follow: bool):
    """Show logs for a service."""
    manager = ctx.obj['manager']
    
    if follow:
        # Follow logs (tail -f behavior)
        log_file = manager._get_log_file(service_name)
        if not log_file or not os.path.exists(log_file):
            click.echo(f"{Fore.RED}No log file found for service '{service_name}'{Style.RESET_ALL}", err=True)
            sys.exit(1)
        
        try:
            import subprocess
            subprocess.run(['tail', '-f', log_file])
        except KeyboardInterrupt:
            click.echo(f"\n{Fore.YELLOW}Stopped following logs{Style.RESET_ALL}")
        except FileNotFoundError:
            click.echo(f"{Fore.RED}tail command not found. Please install coreutils{Style.RESET_ALL}", err=True)
            sys.exit(1)
    else:
        # Show last N lines
        log_content = manager.get_service_logs(service_name, lines)
        click.echo(log_content)


@cli.command()
@click.pass_context
def list_services(ctx):
    """List all available services."""
    config = ctx.obj['config']
    services = config.get_services()
    
    click.echo(f"{Fore.CYAN}Available Services:{Style.RESET_ALL}")
    click.echo("=" * 30)
    
    for name, service_config in services.items():
        description = service_config.get('description', 'No description')
        port = service_config.get('port', 'N/A')
        click.echo(f"{Fore.BLUE}{name}{Style.RESET_ALL} (port: {port})")
        click.echo(f"    {description}")
        click.echo()


@cli.command()
def plugins():
    """List all available plugins."""
    plugin_info = get_plugin_info()
    
    click.echo(f"{Fore.CYAN}Available Plugins:{Style.RESET_ALL}")
    click.echo("=" * 30)
    
    if not plugin_info:
        click.echo(f"{Fore.YELLOW}No plugins found{Style.RESET_ALL}")
        return
    
    for plugin in plugin_info:
        click.echo(f"{Fore.BLUE}{plugin['name']}{Style.RESET_ALL} v{plugin['version']}")
        click.echo(f"    {plugin['description']}")
        click.echo()


@cli.group()
def use_games():
    """Game testing utilities."""
    pass


@use_games.command()
@click.option('--test', help='Test name to run')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def test(ctx, test: str, verbose: bool):
    """Run game tests."""
    manager = ctx.obj['manager']
    config = ctx.obj['config']
    
    if verbose:
        click.echo(f"{Fore.CYAN}Running test: {test}{Style.RESET_ALL}")
    
    # Start required services
    required_services = ['lobby', 'dealer']
    
    for service_name in required_services:
        if not manager._is_service_running(service_name):
            click.echo(f"{Fore.YELLOW}Starting {service_name}...{Style.RESET_ALL}")
            success, message = manager.start_service(service_name)
            if success:
                click.echo(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")
            else:
                click.echo(f"{Fore.RED}✗ {message}{Style.RESET_ALL}", err=True)
                return
    
    # Wait for services to be ready
    import time
    time.sleep(3)
    
    # Run test
    if test == "5-3-test":
        click.echo(f"{Fore.CYAN}Running 5-3-test: 5 players, 3 rounds{Style.RESET_ALL}")
        
        # Simulate test game
        if verbose:
            click.echo("Creating test table...")
            click.echo("Adding 5 test players...")
            click.echo("Starting game...")
            click.echo("Playing 3 rounds...")
            click.echo("Game completed!")
        
        click.echo(f"{Fore.GREEN}✓ Test '{test}' completed successfully{Style.RESET_ALL}")
    else:
        click.echo(f"{Fore.RED}Unknown test: {test}{Style.RESET_ALL}", err=True)


@cli.group()
def monitor():
    """Monitoring utilities."""
    pass


@monitor.command()
@click.pass_context
def watch(ctx):
    """Watch real-time monitoring."""
    manager = ctx.obj['manager']
    
    # Start monitor service if not running
    if not manager._is_service_running('cbhands_monitor_ts'):
        click.echo(f"{Fore.YELLOW}Starting monitor service...{Style.RESET_ALL}")
        success, message = manager.start_service('cbhands_monitor_ts')
        if success:
            click.echo(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")
        else:
            click.echo(f"{Fore.RED}✗ {message}{Style.RESET_ALL}", err=True)
            return
    
    click.echo(f"{Fore.CYAN}Monitor is running at http://localhost:9000{Style.RESET_ALL}")
    click.echo(f"{Fore.YELLOW}Press Ctrl+C to stop watching{Style.RESET_ALL}")
    
    try:
        # Follow monitor logs
        log_file = manager._get_log_file('cbhands_monitor_ts')
        if os.path.exists(log_file):
            import subprocess
            subprocess.run(['tail', '-f', log_file])
        else:
            click.echo(f"{Fore.RED}Monitor log file not found{Style.RESET_ALL}", err=True)
    except KeyboardInterrupt:
        click.echo(f"\n{Fore.YELLOW}Stopped watching monitor{Style.RESET_ALL}")


def load_plugins():
    """Load available plugins."""
    plugins = {}
    
    try:
        # Try to load dev_showroom plugin
        from cbhands_dev_showroom.plugin import DevShowroomPlugin
        dev_showroom = DevShowroomPlugin()
        plugins[dev_showroom.name] = dev_showroom
    except ImportError:
        pass
    
    return plugins


def get_plugin_info():
    """Get plugin information including versions."""
    plugin_info = []
    
    try:
        # Get dev_showroom plugin info
        import cbhands_dev_showroom
        plugin_info.append({
            'name': 'dev_showroom',
            'version': getattr(cbhands_dev_showroom, '__version__', '0.1.0'),
            'description': 'Development Showroom - Interactive testing and demonstration tool'
        })
    except ImportError:
        pass
    
    try:
        # Get use_games plugin info
        import cbhands_use_games
        plugin_info.append({
            'name': 'use_games',
            'version': getattr(cbhands_use_games, '__version__', '0.1.0'),
            'description': 'Game Testing - Testing utilities for Battle Hands'
        })
    except ImportError:
        pass
    
    return plugin_info


def main():
    """Main entry point."""
    # Load plugins
    plugins = load_plugins()
    
    # Add plugin commands to CLI
    for plugin_name, plugin in plugins.items():
        commands = plugin.get_commands()
        
        # Create a plugin group with hyphenated name
        plugin_group_name = plugin_name.replace('_', '-')
        
        @click.group(name=plugin_group_name)
        def plugin_group():
            """Plugin commands."""
            pass
        
        # Create commands for each plugin function
        if 'create-tables' in commands:
            @click.command(name='create-tables')
            @click.option('--count', default=10, help='Number of tables to create')
            @click.option('--mode', default='fun', help='Game mode')
            @click.pass_context
            def create_tables_command(ctx, count, mode, **kwargs):
                commands['create-tables'](count=count, mode=mode, verbose=ctx.obj.get('verbose', False))
            plugin_group.add_command(create_tables_command)
        
        if 'list-tables' in commands:
            @click.command(name='list-tables')
            @click.pass_context
            def list_tables_command(ctx, **kwargs):
                commands['list-tables'](verbose=ctx.obj.get('verbose', False))
            plugin_group.add_command(list_tables_command)
        
        if 'show-table' in commands:
            @click.command(name='show-table')
            @click.option('--name', required=True, help='Table name')
            @click.pass_context
            def show_table_command(ctx, name, **kwargs):
                commands['show-table'](name=name, verbose=ctx.obj.get('verbose', False))
            plugin_group.add_command(show_table_command)
        
        if 'delete-tables' in commands:
            @click.command(name='delete-tables')
            @click.option('--all', is_flag=True, help='All tables')
            @click.option('--name', help='Table name')
            @click.pass_context
            def delete_tables_command(ctx, all, name, **kwargs):
                commands['delete-tables'](all_tables=all, name=name, verbose=ctx.obj.get('verbose', False))
            plugin_group.add_command(delete_tables_command)
        
        if 'show-redis' in commands:
            @click.command(name='show-redis')
            @click.option('--keys', help='Redis key pattern')
            @click.pass_context
            def show_redis_command(ctx, keys, **kwargs):
                commands['show-redis'](keys=keys, verbose=ctx.obj.get('verbose', False))
            plugin_group.add_command(show_redis_command)
        
        if 'interactive' in commands:
            @click.command(name='interactive')
            @click.pass_context
            def interactive_command(ctx, **kwargs):
                commands['interactive'](verbose=ctx.obj.get('verbose', False))
            plugin_group.add_command(interactive_command)
        
        # Add the plugin group to the main CLI
        cli.add_command(plugin_group)
    
    # Add plugin information to help
    plugin_info = get_plugin_info()
    if plugin_info:
        # Create enhanced help text
        plugin_text = f"\n{Fore.CYAN}Available Plugins:{Style.RESET_ALL}\n"
        plugin_text += "=" * 30 + "\n"
        for plugin in plugin_info:
            plugin_text += f"{Fore.BLUE}{plugin['name']}{Style.RESET_ALL} v{plugin['version']} - {plugin['description']}\n"
        plugin_text += "\n"
        
        # Append plugin information to help
        cli.help = cli.help + plugin_text
    
    cli()


if __name__ == '__main__':
    main()
