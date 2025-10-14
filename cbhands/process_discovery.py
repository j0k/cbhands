"""Process discovery and management for cbhands v2.1."""

import os
import time
import psutil
import subprocess
import yaml
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

from .logger import get_logger

logger = get_logger(__name__)


@dataclass
class DiscoveredProcess:
    """Represents a discovered process."""
    pid: int
    name: str
    command: str
    working_directory: str
    port: Optional[int]
    service_type: str
    parent_pid: Optional[int]
    children: List[int]
    cpu_percent: float
    memory_percent: float
    create_time: float
    uptime: str


class ProcessDiscovery:
    """Discovers and manages Battle Hands processes."""
    
    def __init__(self, config_dir: str = "/tmp"):
        """Initialize process discovery.
        
        Args:
            config_dir: Directory for temporary files
        """
        self.config_dir = config_dir
        self.discovered_file = os.path.join(config_dir, "cbhands_discovered_processes.yaml")
        
        # Battle Hands service patterns
        self.service_patterns = {
            'lobby': {
                'command_patterns': ['go run cmd/lobby/main.go', 'main.*lobby', 'lobby.*main'],
                'port_patterns': [6001],
                'working_dir_patterns': ['/battles/lobby'],
                'process_name_patterns': ['main', 'lobby']
            },
            'dealer': {
                'command_patterns': ['go run cmd/dealer/main.go', 'main.*dealer', 'dealer.*main'],
                'port_patterns': [6000],
                'working_dir_patterns': ['/battles/dealer'],
                'process_name_patterns': ['main', 'dealer']
            },
            'monitor': {
                'command_patterns': ['node dist/index.js', 'monitor.*node', 'node.*monitor'],
                'port_patterns': [9001, 9000],
                'working_dir_patterns': ['/battles/cbhands_monitor_ts'],
                'process_name_patterns': ['node']
            },
            'frontend': {
                'command_patterns': ['serve dist', 'npx serve', 'serve.*dist'],
                'port_patterns': [3000],
                'working_dir_patterns': ['/battles/battle_hands_ts'],
                'process_name_patterns': ['serve', 'node']
            }
        }
    
    def discover_all_processes(self) -> Dict[str, DiscoveredProcess]:
        """Discover all Battle Hands processes.
        
        Returns:
            Dictionary of discovered processes by service type
        """
        discovered = {}
        
        try:
            # Get all running processes
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cwd', 'create_time', 'cpu_percent', 'memory_percent', 'ppid']):
                try:
                    proc_info = proc.info
                    if not proc_info['cmdline']:
                        continue
                    
                    command = ' '.join(proc_info['cmdline'])
                    working_dir = proc_info['cwd'] or ''
                    
                    # Check each service type
                    for service_type, patterns in self.service_patterns.items():
                        if self._matches_patterns(command, working_dir, patterns):
                            port = self._find_listening_port(proc_info['pid'])
                            
                            discovered_process = DiscoveredProcess(
                                pid=proc_info['pid'],
                                name=proc_info['name'],
                                command=command,
                                working_directory=working_dir,
                                port=port,
                                service_type=service_type,
                                parent_pid=proc_info['ppid'],
                                children=self._get_children(proc_info['pid']),
                                cpu_percent=proc_info['cpu_percent'] or 0.0,
                                memory_percent=proc_info['memory_percent'] or 0.0,
                                create_time=proc_info['create_time'],
                                uptime=self._calculate_uptime(proc_info['create_time'])
                            )
                            
                            discovered[service_type] = discovered_process
                            break
                
                except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                    continue
        
        except Exception as e:
            logger.error(f"Error during process discovery: {e}")
        
        # Save discovered processes
        self._save_discovered_processes(discovered)
        
        return discovered
    
    def _matches_patterns(self, command: str, working_dir: str, patterns: Dict[str, List[str]]) -> bool:
        """Check if process matches service patterns."""
        # Check command patterns
        for pattern in patterns['command_patterns']:
            if pattern.lower() in command.lower():
                return True
        
        # Check working directory patterns
        for pattern in patterns['working_dir_patterns']:
            if pattern in working_dir:
                return True
        
        return False
    
    def _find_listening_port(self, pid: int) -> Optional[int]:
        """Find the port a process is listening on."""
        try:
            # Use netstat to find listening ports
            result = subprocess.run(['netstat', '-tlnp'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if f'{pid}/' in line and 'LISTEN' in line:
                    # Extract port from the line
                    parts = line.split()
                    if len(parts) >= 4:
                        addr = parts[3]
                        if ':' in addr:
                            port = int(addr.split(':')[-1])
                            return port
        except Exception as e:
            logger.debug(f"Error finding port for PID {pid}: {e}")
        
        return None
    
    def _get_children(self, pid: int) -> List[int]:
        """Get child process IDs."""
        try:
            proc = psutil.Process(pid)
            return [child.pid for child in proc.children(recursive=False)]
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return []
    
    def _calculate_uptime(self, create_time: float) -> str:
        """Calculate process uptime."""
        try:
            uptime_seconds = time.time() - create_time
            hours = int(uptime_seconds // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            seconds = int(uptime_seconds % 60)
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        except:
            return "00:00:00"
    
    def _save_discovered_processes(self, processes: Dict[str, DiscoveredProcess]):
        """Save discovered processes to file."""
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'processes': {}
            }
            
            for service_type, proc in processes.items():
                data['processes'][service_type] = {
                    'pid': proc.pid,
                    'name': proc.name,
                    'command': proc.command,
                    'working_directory': proc.working_directory,
                    'port': proc.port,
                    'service_type': proc.service_type,
                    'parent_pid': proc.parent_pid,
                    'children': proc.children,
                    'cpu_percent': proc.cpu_percent,
                    'memory_percent': proc.memory_percent,
                    'create_time': proc.create_time,
                    'uptime': proc.uptime
                }
            
            with open(self.discovered_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False)
                
        except Exception as e:
            logger.error(f"Error saving discovered processes: {e}")
    
    def load_discovered_processes(self) -> Dict[str, DiscoveredProcess]:
        """Load discovered processes from file."""
        if not os.path.exists(self.discovered_file):
            return {}
        
        try:
            with open(self.discovered_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            processes = {}
            for service_type, proc_data in data.get('processes', {}).items():
                processes[service_type] = DiscoveredProcess(
                    pid=proc_data['pid'],
                    name=proc_data['name'],
                    command=proc_data['command'],
                    working_directory=proc_data['working_directory'],
                    port=proc_data['port'],
                    service_type=proc_data['service_type'],
                    parent_pid=proc_data['parent_pid'],
                    children=proc_data['children'],
                    cpu_percent=proc_data['cpu_percent'],
                    memory_percent=proc_data['memory_percent'],
                    create_time=proc_data['create_time'],
                    uptime=proc_data['uptime']
                )
            
            return processes
            
        except Exception as e:
            logger.error(f"Error loading discovered processes: {e}")
            return {}
    
    def kill_orphaned_processes(self) -> List[int]:
        """Kill orphaned Battle Hands processes."""
        killed_pids = []
        
        try:
            discovered = self.discover_all_processes()
            
            for service_type, proc in discovered.items():
                try:
                    # Check if process is still running
                    if psutil.pid_exists(proc.pid):
                        psutil.Process(proc.pid).kill()
                        killed_pids.append(proc.pid)
                        logger.info(f"Killed orphaned {service_type} process (PID: {proc.pid})")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        
        except Exception as e:
            logger.error(f"Error killing orphaned processes: {e}")
        
        return killed_pids
