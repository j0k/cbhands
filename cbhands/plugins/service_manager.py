"""Service Manager plugin for cbhands v3.0.0."""

import subprocess
import psutil
import time
import os
from typing import Dict, Any, List, Optional
from pathlib import Path

from ..core import BasePlugin, CommandDefinition, OptionDefinition, OptionType, CommandResult, PluginMetadata
from ..core.config import PluginConfig


class ServiceManagerPlugin(BasePlugin):
    """Plugin for managing Battle Hands services."""
    
    def __init__(self, config: Optional[PluginConfig] = None, event_bus=None):
        """Initialize service manager plugin."""
        super().__init__(config, event_bus)
        self.services = {
            'lobby': {
                'port': 6001,
                'command': 'go run ./cmd/lobby/main.go',
                'working_dir': '/home/jk/battles/lobby',
                'env': {'BYPASS_JWT': '1'}
            },
            'dealer': {
                'port': 6000,
                'command': 'go run ./cmd/dealer/main.go',
                'working_dir': '/home/jk/battles/dealer'
            },
            'frontend': {
                'port': 3000,
                'command': 'npm run serve',
                'working_dir': '/home/jk/battles/battle_hands_ts'
            },
            'monitor': {
                'port': 9001,
                'command': 'node dist/index.js --port 9001',
                'working_dir': '/home/jk/battles/cbhands_monitor_ts',
                'env': {'MONITOR_PORT': '9001'}
            }
        }
        self.pid_files = {}
        self._setup_pid_files()
    
    def _setup_pid_files(self):
        """Setup PID file paths."""
        pid_dir = Path.home() / '.config' / 'cbhands' / 'pids'
        pid_dir.mkdir(parents=True, exist_ok=True)
        
        for service_name in self.services:
            self.pid_files[service_name] = pid_dir / f"{service_name}.pid"
    
    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="service_manager",
            version="1.0.0",
            description="Service management for Battle Hands microservices",
            author="Battle Hands Team",
            dependencies=["psutil"]
        )
    
    def get_commands(self) -> List[CommandDefinition]:
        """Get command definitions."""
        return [
            CommandDefinition(
                name="start",
                description="Start a service",
                handler=self._start_service,
                options=[
                    OptionDefinition(
                        name="service",
                        type=OptionType.CHOICE,
                        description="Service to start",
                        choices=list(self.services.keys()),
                        required=True
                    )
                ],
                group="service"
            ),
            CommandDefinition(
                name="stop",
                description="Stop a service",
                handler=self._stop_service,
                options=[
                    OptionDefinition(
                        name="service",
                        type=OptionType.CHOICE,
                        description="Service to stop",
                        choices=list(self.services.keys()),
                        required=True
                    )
                ],
                group="service"
            ),
            CommandDefinition(
                name="restart",
                description="Restart a service",
                handler=self._restart_service,
                options=[
                    OptionDefinition(
                        name="service",
                        type=OptionType.CHOICE,
                        description="Service to restart",
                        choices=list(self.services.keys()),
                        required=True
                    )
                ],
                group="service"
            ),
            CommandDefinition(
                name="status",
                description="Show service status",
                handler=self._service_status,
                options=[
                    OptionDefinition(
                        name="service",
                        type=OptionType.CHOICE,
                        description="Service to check",
                        choices=list(self.services.keys()) + ['all'],
                        default='all'
                    )
                ],
                group="service"
            ),
            CommandDefinition(
                name="start-all",
                description="Start all services",
                handler=self._start_all_services,
                group="service"
            ),
            CommandDefinition(
                name="stop-all",
                description="Stop all services",
                handler=self._stop_all_services,
                group="service"
            ),
            CommandDefinition(
                name="restart-all",
                description="Restart all services",
                handler=self._restart_all_services,
                group="service"
            )
        ]
    
    def _start_service(self, ctx, **kwargs) -> CommandResult:
        """Start a service."""
        service_name = kwargs['service']
        service_config = self.services[service_name]
        
        # Check if service is already running
        if self._is_service_running(service_name):
            return CommandResult.warning_result(f"Service {service_name} is already running", [])
        
        try:
            # Change to working directory
            working_dir = service_config['working_dir']
            if not os.path.exists(working_dir):
                return CommandResult.error_result(f"Working directory does not exist: {working_dir}")
            
            # Prepare environment
            env = os.environ.copy()
            if 'env' in service_config:
                env.update(service_config['env'])
            
            # Start service
            process = subprocess.Popen(
                service_config['command'],
                shell=True,
                cwd=working_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Save PID
            with open(self.pid_files[service_name], 'w') as f:
                f.write(str(process.pid))
            
            # Wait a bit for service to start
            time.sleep(2)
            
            # Check if service is running
            if self._is_service_running(service_name):
                return CommandResult.success_result(f"Service {service_name} started successfully")
            else:
                return CommandResult.error_result(f"Service {service_name} failed to start")
                
        except Exception as e:
            return CommandResult.error_result(f"Failed to start service {service_name}: {str(e)}")
    
    def _stop_service(self, ctx, **kwargs) -> CommandResult:
        """Stop a service."""
        service_name = kwargs['service']
        
        if not self._is_service_running(service_name):
            return CommandResult.warning_result(f"Service {service_name} is not running", [])
        
        try:
            # Get PID from file
            pid = self._get_service_pid(service_name)
            if pid:
                # Kill process
                process = psutil.Process(pid)
                process.terminate()
                
                # Wait for process to stop
                try:
                    process.wait(timeout=10)
                except psutil.TimeoutExpired:
                    process.kill()
                
                # Remove PID file
                if self.pid_files[service_name].exists():
                    self.pid_files[service_name].unlink()
                
                return CommandResult.success_result(f"Service {service_name} stopped successfully")
            else:
                return CommandResult.error_result(f"Could not find PID for service {service_name}")
                
        except Exception as e:
            return CommandResult.error_result(f"Failed to stop service {service_name}: {str(e)}")
    
    def _restart_service(self, ctx, **kwargs) -> CommandResult:
        """Restart a service."""
        service_name = kwargs['service']
        
        # Stop service first
        stop_result = self._stop_service(ctx, **kwargs)
        if not stop_result.success and "not running" not in stop_result.message:
            return stop_result
        
        # Start service
        return self._start_service(ctx, **kwargs)
    
    def _service_status(self, ctx, **kwargs) -> CommandResult:
        """Show service status."""
        service_name = kwargs['service']
        
        if service_name == 'all':
            status_data = {}
            for svc in self.services:
                status_data[svc] = self._get_service_info(svc)
            
            return CommandResult.success_result("Service Status", data=status_data)
        else:
            info = self._get_service_info(service_name)
            return CommandResult.success_result(f"Service {service_name} status", data=info)
    
    def _start_all_services(self, ctx, **kwargs) -> CommandResult:
        """Start all services."""
        results = {}
        for service_name in self.services:
            result = self._start_service(ctx, service=service_name)
            results[service_name] = result.success
        
        success_count = sum(results.values())
        total_count = len(results)
        
        if success_count == total_count:
            return CommandResult.success_result(f"All {total_count} services started successfully")
        else:
            return CommandResult.warning_result(
                f"Started {success_count}/{total_count} services",
                [],
                data=results
            )
    
    def _stop_all_services(self, ctx, **kwargs) -> CommandResult:
        """Stop all services."""
        results = {}
        for service_name in self.services:
            result = self._stop_service(ctx, service=service_name)
            results[service_name] = result.success
        
        success_count = sum(results.values())
        total_count = len(results)
        
        if success_count == total_count:
            return CommandResult.success_result(f"All {total_count} services stopped successfully")
        else:
            return CommandResult.warning_result(
                f"Stopped {success_count}/{total_count} services",
                [],
                data=results
            )
    
    def _restart_all_services(self, ctx, **kwargs) -> CommandResult:
        """Restart all services."""
        # Stop all first
        stop_result = self._stop_all_services(ctx, **kwargs)
        
        # Start all
        start_result = self._start_all_services(ctx, **kwargs)
        
        if stop_result.success and start_result.success:
            return CommandResult.success_result("All services restarted successfully")
        else:
            return CommandResult.warning_result("Some services may not have restarted properly", [])
    
    def _is_service_running(self, service_name: str) -> bool:
        """Check if service is running."""
        try:
            # Check PID file
            pid = self._get_service_pid(service_name)
            if pid:
                process = psutil.Process(pid)
                return process.is_running()
            
            # Check by port
            service_config = self.services[service_name]
            port = service_config['port']
            
            for conn in psutil.net_connections():
                if conn.laddr.port == port and conn.status == 'LISTEN':
                    return True
            
            return False
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False
    
    def _get_service_pid(self, service_name: str) -> Optional[int]:
        """Get service PID from file."""
        try:
            if self.pid_files[service_name].exists():
                with open(self.pid_files[service_name], 'r') as f:
                    return int(f.read().strip())
        except (ValueError, FileNotFoundError):
            pass
        return None
    
    def _get_service_info(self, service_name: str) -> Dict[str, Any]:
        """Get detailed service information."""
        service_config = self.services[service_name]
        is_running = self._is_service_running(service_name)
        pid = self._get_service_pid(service_name) if is_running else None
        
        return {
            'name': service_name,
            'running': is_running,
            'pid': pid,
            'port': service_config['port'],
            'command': service_config['command'],
            'working_dir': service_config['working_dir']
        }
