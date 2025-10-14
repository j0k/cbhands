"""Service manager for cbhands."""

import os
import time
import signal
import subprocess
import psutil
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import yaml

from .config import Config
from .logger import get_logger

logger = get_logger(__name__)


class ServiceManager:
    """Manager for Battle Hands services."""
    
    def __init__(self, config: Config):
        """Initialize service manager.
        
        Args:
            config: Configuration instance
        """
        self.config = config
        self.state_file = config.get_state_file_path()
        self.log_dir = config.get_log_dir()
        self.pid_dir = config.get_pid_dir()
        
        # Ensure directories exist
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.pid_dir, exist_ok=True)
        
        # Load current state
        self.state = self._load_state()
    
    def _load_state(self) -> Dict[str, Any]:
        """Load current state from state file."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                logger.warning(f"Failed to load state file: {e}")
        return {}
    
    def _save_state(self):
        """Save current state to state file."""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.state, f, default_flow_style=False)
        except Exception as e:
            logger.error(f"Failed to save state file: {e}")
    
    def _get_pid_file(self, service_name: str) -> str:
        """Get PID file path for service."""
        return os.path.join(self.pid_dir, f"{service_name}.pid")
    
    def _get_log_file(self, service_name: str) -> str:
        """Get log file path for service."""
        return os.path.join(self.log_dir, f"{service_name}.log")
    
    def _is_service_running(self, service_name: str) -> bool:
        """Check if service is running."""
        service_config = self.config.get_service(service_name)
        if not service_config:
            return False
        
        # First check: Look for processes using the expected port
        port = service_config.get('port')
        if port and self._is_port_in_use(port):
            return True
        
        # Second check: Check PID file and process
        pid_file = self._get_pid_file(service_name)
        if not os.path.exists(pid_file):
            return False
        
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process is still running
            if psutil.pid_exists(pid):
                process = psutil.Process(pid)
                # Check if it's still the same command
                cmd = ' '.join(process.cmdline())
                expected_cmd = service_config.get('command', '')
                if (service_config['name'] in cmd or 
                    expected_cmd in cmd or 
                    cmd.endswith(expected_cmd.split()[-1])):
                    return True
            
            # Third check: Look for child processes that might be running the service
            return self._check_child_processes(service_name, port)
            
        except (ValueError, psutil.NoSuchProcess, psutil.AccessDenied):
            # If PID file exists but process is dead, check for child processes
            return self._check_child_processes(service_name, port)
    
    def _is_port_in_use(self, port: int) -> bool:
        """Check if a port is in use."""
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', port))
                return result == 0
        except:
            return False
    
    def _check_child_processes(self, service_name: str, port: int) -> bool:
        """Check for child processes that might be running the service."""
        if not port:
            return False
        
        try:
            # Check if port is in use by any process
            if self._is_port_in_use(port):
                # Find which process is using the port
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        if proc.info['cmdline']:
                            cmdline = ' '.join(proc.info['cmdline'])
                            # Check if this looks like our service
                            if (service_name in cmdline or 
                                'serve' in cmdline or 
                                'node' in cmdline and str(port) in cmdline):
                                return True
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
        except:
            pass
        
        return False
    
    def _get_service_pid(self, service_name: str) -> Optional[int]:
        """Get PID of running service."""
        if not self._is_service_running(service_name):
            return None
        
        service_config = self.config.get_service(service_name)
        if not service_config:
            return None
        
        port = service_config.get('port')
        
        # First try to get PID from file
        try:
            with open(self._get_pid_file(service_name), 'r') as f:
                pid = int(f.read().strip())
                if psutil.pid_exists(pid):
                    return pid
        except (ValueError, FileNotFoundError):
            pass
        
        # If PID file is outdated, find the actual running process by port
        if port:
            try:
                # Use netstat to find the process listening on the port
                import subprocess
                result = subprocess.run(['netstat', '-tlnp'], capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if f':{port}' in line and 'LISTEN' in line:
                        # Extract PID from the line
                        parts = line.split()
                        if len(parts) >= 7:
                            pid_part = parts[6].split('/')[0]
                            try:
                                pid = int(pid_part)
                                return pid
                            except ValueError:
                                continue
            except:
                pass
            
            # Fallback: search through processes
            try:
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        if proc.info['cmdline']:
                            cmdline = ' '.join(proc.info['cmdline'])
                            if (service_name in cmdline or 
                                ('serve' in cmdline and '3000' in cmdline) or
                                ('node' in cmdline and 'dist/index.js' in cmdline) or
                                ('main' in cmdline and ('lobby' in cmdline or 'dealer' in cmdline))):
                                return proc.info['pid']
                    except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                        continue
            except:
                pass
        
        return None
    
    def start_service(self, service_name: str) -> Tuple[bool, str]:
        """Start a service.
        
        Args:
            service_name: Name of service to start
            
        Returns:
            Tuple of (success, message)
        """
        service_config = self.config.get_service(service_name)
        if not service_config:
            return False, f"Service '{service_name}' not found in configuration"
        
        if self._is_service_running(service_name):
            return False, f"Service '{service_name}' is already running"
        
        try:
            # Prepare command
            if '&&' in service_config['command'] or '|' in service_config['command']:
                # Use shell for complex commands
                cmd = ['sh', '-c', service_config['command']]
            else:
                # Split command for direct execution
                cmd = service_config['command'].split()
            
            # Start process
            process = subprocess.Popen(
                cmd,
                cwd=service_config['working_directory'],
                stdout=open(self._get_log_file(service_name), 'a'),
                stderr=subprocess.STDOUT,
                env={**os.environ, **{k: str(v) for k, v in service_config.get('env', {}).items()}},
                preexec_fn=os.setsid if '&&' in service_config['command'] or '|' in service_config['command'] else None
            )
            
            # Save PID
            with open(self._get_pid_file(service_name), 'w') as f:
                f.write(str(process.pid))
            
            # Update state
            self.state[service_name] = {
                'pid': process.pid,
                'started_at': time.time(),
                'status': 'running',
                'config': service_config
            }
            self._save_state()
            
            logger.info(f"Started service '{service_name}' with PID {process.pid}")
            return True, f"Service '{service_name}' started successfully (PID: {process.pid})"
            
        except Exception as e:
            logger.error(f"Failed to start service '{service_name}': {e}")
            return False, f"Failed to start service '{service_name}': {e}"
    
    def stop_service(self, service_name: str) -> Tuple[bool, str]:
        """Stop a service.
        
        Args:
            service_name: Name of service to stop
            
        Returns:
            Tuple of (success, message)
        """
        if not self._is_service_running(service_name):
            return False, f"Service '{service_name}' is not running"
        
        try:
            pid = self._get_service_pid(service_name)
            if not pid:
                return False, f"Could not find PID for service '{service_name}'"
            
            # Terminate process
            process = psutil.Process(pid)
            process.terminate()
            
            # Wait for graceful shutdown
            try:
                process.wait(timeout=5)
            except psutil.TimeoutExpired:
                # Force kill if graceful shutdown failed
                process.kill()
                process.wait(timeout=2)
            
            # Clean up PID file
            pid_file = self._get_pid_file(service_name)
            if os.path.exists(pid_file):
                os.remove(pid_file)
            
            # Update state
            if service_name in self.state:
                self.state[service_name]['status'] = 'stopped'
                self.state[service_name]['stopped_at'] = time.time()
                self._save_state()
            
            logger.info(f"Stopped service '{service_name}' (PID: {pid})")
            return True, f"Service '{service_name}' stopped successfully"
            
        except psutil.NoSuchProcess:
            # Process already dead
            pid_file = self._get_pid_file(service_name)
            if os.path.exists(pid_file):
                os.remove(pid_file)
            return True, f"Service '{service_name}' was not running"
        except Exception as e:
            logger.error(f"Failed to stop service '{service_name}': {e}")
            return False, f"Failed to stop service '{service_name}': {e}"
    
    def restart_service(self, service_name: str) -> Tuple[bool, str]:
        """Restart a service.
        
        Args:
            service_name: Name of service to restart
            
        Returns:
            Tuple of (success, message)
        """
        # Stop service first
        stop_success, stop_msg = self.stop_service(service_name)
        if not stop_success and "not running" not in stop_msg:
            return False, f"Failed to stop service before restart: {stop_msg}"
        
        # Wait a bit
        time.sleep(1)
        
        # Start service
        start_success, start_msg = self.start_service(service_name)
        if not start_success:
            return False, f"Failed to start service after restart: {start_msg}"
        
        return True, f"Service '{service_name}' restarted successfully"
    
    def get_service_status(self, service_name: str) -> Dict[str, Any]:
        """Get status of a service.
        
        Args:
            service_name: Name of service
            
        Returns:
            Service status information
        """
        service_config = self.config.get_service(service_name)
        if not service_config:
            return {
                'name': service_name,
                'status': 'not_found',
                'message': 'Service not found in configuration'
            }
        
        is_running = self._is_service_running(service_name)
        pid = self._get_service_pid(service_name)
        
        status_info = {
            'name': service_name,
            'status': 'running' if is_running else 'stopped',
            'pid': pid,
            'port': service_config['port'],
            'description': service_config['description'],
            'config': service_config
        }
        
        if is_running and service_name in self.state:
            status_info.update({
                'started_at': self.state[service_name].get('started_at'),
                'uptime': time.time() - self.state[service_name].get('started_at', time.time())
            })
        
        return status_info
    
    def get_all_services_status(self) -> List[Dict[str, Any]]:
        """Get status of all services.
        
        Returns:
            List of service status information
        """
        services = self.config.get_services()
        return [self.get_service_status(name) for name in services.keys()]
    
    def get_service_logs(self, service_name: str, lines: int = 100) -> str:
        """Get logs for a service.
        
        Args:
            service_name: Name of service
            lines: Number of lines to return
            
        Returns:
            Log content
        """
        log_file = self._get_log_file(service_name)
        if not os.path.exists(log_file):
            return f"No log file found for service '{service_name}'"
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                return ''.join(all_lines[-lines:])
        except Exception as e:
            return f"Error reading logs for service '{service_name}': {e}"
    
    def stop_all_services(self) -> Tuple[bool, str]:
        """Stop all Battle Hands services.
        
        Returns:
            Tuple of (success, message)
        """
        services = self.config.get_services()
        stopped_services = []
        failed_services = []
        
        for service_name in services.keys():
            success, message = self.stop_service(service_name)
            if success:
                stopped_services.append(service_name)
            else:
                failed_services.append(service_name)
        
        if not failed_services:
            return True, f"All services stopped successfully: {', '.join(stopped_services)}"
        elif stopped_services:
            return False, f"Partially stopped: {', '.join(stopped_services)}. Failed: {', '.join(failed_services)}"
        else:
            return False, f"Failed to stop all services: {', '.join(failed_services)}"
    
    def start_all_services(self) -> Tuple[bool, str]:
        """Start all Battle Hands services.
        
        Returns:
            Tuple of (success, message)
        """
        services = self.config.get_services()
        started_services = []
        failed_services = []
        
        for service_name in services.keys():
            success, message = self.start_service(service_name)
            if success:
                started_services.append(service_name)
            else:
                failed_services.append(service_name)
        
        if not failed_services:
            return True, f"All services started successfully: {', '.join(started_services)}"
        elif started_services:
            return False, f"Partially started: {', '.join(started_services)}. Failed: {', '.join(failed_services)}"
        else:
            return False, f"Failed to start all services: {', '.join(failed_services)}"
