"""Tests for cbhands v3.0.0 core functionality."""

import pytest
from unittest.mock import Mock, patch

from cbhands.v3.core import (
    BasePlugin, BaseCommand, CommandDefinition, OptionDefinition, OptionType, CommandResult,
    PluginMetadata, PluginRegistry, EventBus, PluginConfig
)


class TestCommandDefinition:
    """Test CommandDefinition class."""
    
    def test_command_definition_creation(self):
        """Test creating command definition."""
        cmd_def = CommandDefinition(
            name="test",
            description="Test command",
            handler=lambda: None
        )
        
        assert cmd_def.name == "test"
        assert cmd_def.description == "Test command"
        assert cmd_def.handler is not None
        assert cmd_def.options == []
        assert cmd_def.group is None
        assert cmd_def.hidden is False
    
    def test_command_definition_with_options(self):
        """Test command definition with options."""
        options = [
            OptionDefinition(
                name="test_option",
                type=OptionType.STRING,
                description="Test option",
                default="default_value"
            )
        ]
        
        cmd_def = CommandDefinition(
            name="test",
            description="Test command",
            handler=lambda: None,
            options=options
        )
        
        assert len(cmd_def.options) == 1
        assert cmd_def.options[0].name == "test_option"


class TestOptionDefinition:
    """Test OptionDefinition class."""
    
    def test_option_definition_creation(self):
        """Test creating option definition."""
        opt_def = OptionDefinition(
            name="test",
            type=OptionType.STRING,
            description="Test option"
        )
        
        assert opt_def.name == "test"
        assert opt_def.type == OptionType.STRING
        assert opt_def.description == "Test option"
        assert opt_def.default is None
        assert opt_def.required is False


class TestCommandResult:
    """Test CommandResult class."""
    
    def test_success_result(self):
        """Test creating success result."""
        result = CommandResult.success_result("Success message", {"key": "value"})
        
        assert result.success is True
        assert result.message == "Success message"
        assert result.data == {"key": "value"}
        assert result.exit_code == 0
    
    def test_error_result(self):
        """Test creating error result."""
        result = CommandResult.error_result("Error message", 1, ["error1", "error2"])
        
        assert result.success is False
        assert result.message == "Error message"
        assert result.exit_code == 1
        assert result.errors == ["error1", "error2"]
    
    def test_warning_result(self):
        """Test creating warning result."""
        result = CommandResult.warning_result("Warning message", ["warning1"], {"key": "value"})
        
        assert result.success is True
        assert result.message == "Warning message"
        assert result.warnings == ["warning1"]
        assert result.data == {"key": "value"}


class TestPluginMetadata:
    """Test PluginMetadata class."""
    
    def test_plugin_metadata_creation(self):
        """Test creating plugin metadata."""
        metadata = PluginMetadata(
            name="test_plugin",
            version="1.0.0",
            description="Test plugin"
        )
        
        assert metadata.name == "test_plugin"
        assert metadata.version == "1.0.0"
        assert metadata.description == "Test plugin"
        assert metadata.author is None


class TestEventBus:
    """Test EventBus class."""
    
    def test_event_bus_creation(self):
        """Test creating event bus."""
        event_bus = EventBus()
        assert event_bus is not None
    
    def test_subscribe_and_emit(self):
        """Test subscribing to and emitting events."""
        event_bus = EventBus()
        handler_called = []
        
        def handler(event):
            handler_called.append(event)
        
        event_bus.subscribe("test.event", handler)
        event_bus.emit("test.event", {"data": "test"})
        
        assert len(handler_called) == 1
        assert handler_called[0].type == "test.event"
        assert handler_called[0].data == {"data": "test"}
    
    def test_unsubscribe(self):
        """Test unsubscribing from events."""
        event_bus = EventBus()
        handler_called = []
        
        def handler(event):
            handler_called.append(event)
        
        event_bus.subscribe("test.event", handler)
        event_bus.unsubscribe("test.event", handler)
        event_bus.emit("test.event", {"data": "test"})
        
        assert len(handler_called) == 0


class TestPluginRegistry:
    """Test PluginRegistry class."""
    
    def test_plugin_registry_creation(self):
        """Test creating plugin registry."""
        registry = PluginRegistry()
        assert registry is not None
    
    def test_register_plugin(self):
        """Test registering a plugin."""
        registry = PluginRegistry()
        
        # Create mock plugin
        plugin = Mock(spec=BasePlugin)
        plugin.get_metadata.return_value = PluginMetadata(
            name="test_plugin",
            version="1.0.0",
            description="Test plugin"
        )
        plugin.get_commands.return_value = [
            CommandDefinition(
                name="test_command",
                description="Test command",
                handler=lambda: None
            )
        ]
        plugin.get_dependencies.return_value = []
        
        registry.register_plugin(plugin)
        
        assert "test_plugin" in registry.list_plugins()
        assert "test_command" in registry.list_commands()
        assert registry.get_plugin("test_plugin") == plugin
    
    def test_unregister_plugin(self):
        """Test unregistering a plugin."""
        registry = PluginRegistry()
        
        # Create and register mock plugin
        plugin = Mock(spec=BasePlugin)
        plugin.get_metadata.return_value = PluginMetadata(
            name="test_plugin",
            version="1.0.0",
            description="Test plugin"
        )
        plugin.get_commands.return_value = []
        plugin.get_dependencies.return_value = []
        
        registry.register_plugin(plugin)
        registry.unregister_plugin("test_plugin")
        
        assert "test_plugin" not in registry.list_plugins()


class TestPluginConfig:
    """Test PluginConfig class."""
    
    def test_plugin_config_creation(self):
        """Test creating plugin config."""
        config = PluginConfig("test_plugin", {"key": "value"})
        
        assert config.name == "test_plugin"
        assert config.config == {"key": "value"}
        assert config.enabled is True
        assert config.priority == 0
    
    def test_get_and_set(self):
        """Test getting and setting config values."""
        config = PluginConfig("test_plugin")
        
        config.set("key", "value")
        assert config.get("key") == "value"
        assert config.get("nonexistent", "default") == "default"
    
    def test_nested_config(self):
        """Test nested configuration."""
        config = PluginConfig("test_plugin")
        
        config.set_nested("level1.level2.key", "value")
        assert config.get_nested("level1.level2.key") == "value"
        assert config.get_nested("level1.level2.nonexistent", "default") == "default"
    
    def test_merge_configs(self):
        """Test merging configurations."""
        config1 = PluginConfig("test_plugin", {"key1": "value1", "nested": {"key": "value"}})
        config2 = PluginConfig("test_plugin", {"key2": "value2", "nested": {"key2": "value2"}})
        
        config1.merge(config2)
        
        assert config1.get("key1") == "value1"
        assert config1.get("key2") == "value2"
        assert config1.get_nested("nested.key") == "value"
        assert config1.get_nested("nested.key2") == "value2"
