"""Tests for config module."""

import os
import tempfile
import pytest
from pathlib import Path

from cbhands.config import Config


def test_config_loading():
    """Test configuration loading."""
    # Create temporary config file
    config_content = """
services:
  test_service:
    name: "test_service"
    port: 8080
    command: "echo test"
    working_directory: "/tmp"
    health_endpoint: "/health"
    description: "Test service"

settings:
  state_file: "/tmp/test_state.yaml"
  log_dir: "/tmp/test_logs"
  timeout: 30
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        config_path = f.name
    
    try:
        config = Config(config_path)
        
        # Test service loading
        services = config.get_services()
        assert 'test_service' in services
        assert services['test_service']['port'] == 8080
        
        # Test specific service
        service = config.get_service('test_service')
        assert service is not None
        assert service['name'] == 'test_service'
        
        # Test settings
        assert config.get_setting('timeout') == 30
        assert config.get_setting('nonexistent', 'default') == 'default'
        
        # Test paths
        assert config.get_state_file_path() == '/tmp/test_state.yaml'
        assert config.get_log_dir() == '/tmp/test_logs'
        
    finally:
        os.unlink(config_path)


def test_config_nonexistent_file():
    """Test configuration with nonexistent file."""
    with pytest.raises(FileNotFoundError):
        Config('/nonexistent/path.yaml')


def test_config_invalid_yaml():
    """Test configuration with invalid YAML."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write('invalid: yaml: content: [')
        config_path = f.name
    
    try:
        with pytest.raises(RuntimeError):
            Config(config_path)
    finally:
        os.unlink(config_path)
