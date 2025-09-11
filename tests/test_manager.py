"""Tests for manager module."""

import os
import tempfile
import time
import pytest
from unittest.mock import patch, MagicMock

from cbhands.config import Config
from cbhands.manager import ServiceManager


@pytest.fixture
def temp_config():
    """Create temporary configuration for testing."""
    config_content = """
services:
  test_service:
    name: "test_service"
    port: 8080
    command: "sleep 10"
    working_directory: "/tmp"
    health_endpoint: "/health"
    description: "Test service"

settings:
  state_file: "/tmp/test_state.yaml"
  log_dir: "/tmp/test_logs"
  pid_dir: "/tmp/test_pids"
  timeout: 5
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        config_path = f.name
    
    yield config_path
    
    # Cleanup
    if os.path.exists(config_path):
        os.unlink(config_path)


@pytest.fixture
def manager(temp_config):
    """Create service manager for testing."""
    config = Config(temp_config)
    return ServiceManager(config)


def test_manager_initialization(manager):
    """Test manager initialization."""
    assert manager.config is not None
    assert manager.state_file == '/tmp/test_state.yaml'
    assert manager.log_dir == '/tmp/test_logs'
    assert manager.pid_dir == '/tmp/test_pids'


def test_get_service_status_not_found(manager):
    """Test getting status of nonexistent service."""
    status = manager.get_service_status('nonexistent')
    assert status['name'] == 'nonexistent'
    assert status['status'] == 'not_found'


def test_get_service_status_stopped(manager):
    """Test getting status of stopped service."""
    status = manager.get_service_status('test_service')
    assert status['name'] == 'test_service'
    assert status['status'] == 'stopped'
    assert status['port'] == 8080


@patch('subprocess.Popen')
def test_start_service_success(mock_popen, manager):
    """Test successful service start."""
    # Mock process
    mock_process = MagicMock()
    mock_process.pid = 12345
    mock_popen.return_value = mock_process
    
    success, message = manager.start_service('test_service')
    
    assert success is True
    assert 'started successfully' in message
    assert 'PID: 12345' in message
    
    # Check that process was started
    mock_popen.assert_called_once()
    
    # Check that PID file was created
    pid_file = manager._get_pid_file('test_service')
    assert os.path.exists(pid_file)
    
    # Check state
    assert 'test_service' in manager.state
    assert manager.state['test_service']['pid'] == 12345


def test_start_service_not_found(manager):
    """Test starting nonexistent service."""
    success, message = manager.start_service('nonexistent')
    
    assert success is False
    assert 'not found' in message


@patch('psutil.Process')
def test_stop_service_success(mock_process_class, manager):
    """Test successful service stop."""
    # Mock process
    mock_process = MagicMock()
    mock_process_class.return_value = mock_process
    
    # Set up service as running
    manager.state['test_service'] = {
        'pid': 12345,
        'started_at': time.time(),
        'status': 'running'
    }
    
    # Mock PID file
    pid_file = manager._get_pid_file('test_service')
    os.makedirs(os.path.dirname(pid_file), exist_ok=True)
    with open(pid_file, 'w') as f:
        f.write('12345')
    
    # Mock is_service_running to return True
    with patch.object(manager, '_is_service_running', return_value=True):
        success, message = manager.stop_service('test_service')
    
    assert success is True
    assert 'stopped successfully' in message
    
    # Check that process was terminated
    mock_process.terminate.assert_called_once()


def test_stop_service_not_running(manager):
    """Test stopping non-running service."""
    success, message = manager.stop_service('test_service')
    
    assert success is False
    assert 'not running' in message


@patch('subprocess.Popen')
@patch('psutil.Process')
def test_restart_service_success(mock_process_class, mock_popen, manager):
    """Test successful service restart."""
    # Mock process for start
    mock_process = MagicMock()
    mock_process.pid = 12345
    mock_popen.return_value = mock_process
    
    # Mock process for stop
    mock_stop_process = MagicMock()
    mock_process_class.return_value = mock_stop_process
    
    # Set up service as running
    manager.state['test_service'] = {
        'pid': 12345,
        'started_at': time.time(),
        'status': 'running'
    }
    
    # Mock PID file
    pid_file = manager._get_pid_file('test_service')
    os.makedirs(os.path.dirname(pid_file), exist_ok=True)
    with open(pid_file, 'w') as f:
        f.write('12345')
    
    # Mock is_service_running
    with patch.object(manager, '_is_service_running', side_effect=[True, False, False]):
        success, message = manager.restart_service('test_service')
    
    assert success is True
    assert 'restarted successfully' in message


def test_get_all_services_status(manager):
    """Test getting status of all services."""
    all_status = manager.get_all_services_status()
    
    assert len(all_status) == 1
    assert all_status[0]['name'] == 'test_service'
    assert all_status[0]['status'] == 'stopped'


def test_get_service_logs(manager):
    """Test getting service logs."""
    # Create log file
    log_file = manager._get_log_file('test_service')
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    with open(log_file, 'w') as f:
        f.write('Line 1\nLine 2\nLine 3\n')
    
    logs = manager.get_service_logs('test_service', lines=2)
    assert 'Line 2' in logs
    assert 'Line 3' in logs
    assert 'Line 1' not in logs


def test_get_service_logs_nonexistent(manager):
    """Test getting logs for service without log file."""
    logs = manager.get_service_logs('nonexistent')
    assert 'No log file found' in logs
