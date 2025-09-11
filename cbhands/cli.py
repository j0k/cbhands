"""CLI interface for cbhands."""

import sys
import time
from typing import Optional

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
    
    if status == 'running' and pid:
        click.echo(f"    PID: {pid}")
        if port:
            click.echo(f"    Port: {port}")
        
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


def main():
    """Main entry point."""
    cli()


if __name__ == '__main__':
    main()
