# cbhands v3.0.0

**Extensible Service Manager for Battle Hands** - Complete rewrite with focus on extensibility, testability, and maintainability.

## 🚀 What's New in v3.0.0

### ✨ **Major Features**

- **🔌 Declarative Plugin System** - Define plugins through metadata, not hardcoded code
- **📋 Command Groups** - Organize commands into logical groups (e.g., `cbhands dev-showroom tables create`)
- **🔄 Middleware System** - Add hooks for before/after command execution
- **📡 Event Bus** - Plugin communication through events
- **⚙️ Configuration Management** - Per-plugin configuration with validation
- **🔗 Dependency Management** - Plugin dependency resolution
- **🔍 Auto-discovery** - Automatic plugin loading through entry_points
- **⚡ Async Support** - Support for asynchronous commands
- **🎨 Rich Output** - Beautiful console output with colors and tables
- **🔄 Hot-reload** - Development-time plugin reloading
- **📊 Metrics** - Plugin performance monitoring

### 🏗️ **Architecture Improvements**

- **Modular Design** - Clear separation of concerns
- **Type Safety** - Full type hints throughout
- **Testability** - Comprehensive test coverage
- **Extensibility** - Easy to add new features
- **Maintainability** - Clean, readable code

## 📦 Installation

```bash
# Install v3.0.0
pip install cbhands==3.0.0

# With rich formatting
pip install cbhands[rich]==3.0.0

# Development dependencies
pip install cbhands[dev]==3.0.0
```

## 🎯 Quick Start

### Basic Usage

```bash
# List all plugins
cbhands plugins

# Show plugin information
cbhands plugin-info dev-showroom

# List command groups
cbhands groups

# Run commands from plugins
cbhands dev-showroom tables create --count 10
cbhands dev-showroom tables list
```

### Creating a Plugin

```python
from cbhands.v3.core import BasePlugin, CommandDefinition, OptionDefinition, OptionType, CommandResult, PluginMetadata

class MyPlugin(BasePlugin):
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="my_plugin",
            version="1.0.0",
            description="My awesome plugin"
        )
    
    def get_commands(self) -> list[CommandDefinition]:
        return [
            CommandDefinition(
                name="hello",
                description="Say hello",
                handler=self.hello_command,
                options=[
                    OptionDefinition(
                        name="name",
                        type=OptionType.STRING,
                        description="Name to greet",
                        default="World"
                    )
                ]
            )
        ]
    
    def hello_command(self, ctx, **kwargs) -> CommandResult:
        name = kwargs.get('name', 'World')
        return CommandResult.success_result(f"Hello, {name}!")
```

### Plugin Registration

#### Method 1: Entry Points (Recommended)

```python
# setup.py
setup(
    # ...
    entry_points={
        "cbhands.plugins": [
            "my_plugin = my_package.plugin:MyPlugin",
        ],
    },
)
```

#### Method 2: Direct Registration

```python
from cbhands.v3.core import PluginLoader

loader = PluginLoader()
loader.load_plugin("my_plugin", MyPlugin)
```

## 🔧 Configuration

### Plugin Configuration

```yaml
# ~/.config/cbhands/plugins.yaml
plugins:
  my_plugin:
    enabled: true
    priority: 100
    config:
      setting1: "value1"
      setting2: 42
      nested:
        key: "value"
```

### Configuration Schema

```python
class MyPlugin(BasePlugin):
    def get_config_schema(self) -> dict:
        return {
            'type': 'object',
            'properties': {
                'setting1': {
                    'type': 'string',
                    'default': 'default_value'
                },
                'setting2': {
                    'type': 'integer',
                    'minimum': 0,
                    'maximum': 100
                }
            }
        }
    
    def validate_config(self, config: dict) -> list[str]:
        errors = []
        if 'setting2' in config and config['setting2'] > 100:
            errors.append("setting2 must be <= 100")
        return errors
```

## 🎨 Rich Output

cbhands v3.0.0 includes beautiful console output:

```bash
# Install with rich support
pip install cbhands[rich]

# Enjoy colored output, tables, and panels
cbhands plugins --verbose
```

## 🔄 Migration from v2.x

### Automatic Migration

cbhands v3.0.0 includes a compatibility layer for v2.x plugins:

```python
from cbhands.v3.legacy import migrate_legacy_plugin

# Migrate old plugin
new_plugin = migrate_legacy_plugin(old_plugin)
```

### Manual Migration

1. **Update Plugin Class**:
   ```python
   # Old (v2.x)
   class MyPlugin:
       def get_commands(self):
           return {"command": self.command_func}
   
   # New (v3.0.0)
   class MyPlugin(BasePlugin):
       def get_commands(self) -> list[CommandDefinition]:
           return [CommandDefinition(...)]
   ```

2. **Update Command Handlers**:
   ```python
   # Old (v2.x)
   def command_func(self, **kwargs):
       return "Success message"
   
   # New (v3.0.0)
   def command_func(self, ctx, **kwargs) -> CommandResult:
       return CommandResult.success_result("Success message")
   ```

## 🧪 Testing

```bash
# Run tests
pytest tests/

# With coverage
pytest --cov=cbhands tests/

# Run specific test
pytest tests/test_v3/test_core.py::TestCommandDefinition
```

## 📚 API Reference

### Core Classes

- **`BasePlugin`** - Base class for all plugins
- **`BaseCommand`** - Base class for plugin commands
- **`CommandDefinition`** - Command metadata
- **`OptionDefinition`** - Command option metadata
- **`CommandResult`** - Command execution result
- **`PluginMetadata`** - Plugin information
- **`EventBus`** - Event system for plugin communication
- **`PluginRegistry`** - Plugin management
- **`PluginLoader`** - Plugin loading and discovery

### CLI Classes

- **`CLIBuilder`** - Builds Click CLI from plugins
- **`OutputFormatter`** - Output formatting
- **`RichFormatter`** - Rich console output

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- **Documentation**: [GitHub Wiki](https://github.com/j0k/cbhands/wiki)
- **Issues**: [GitHub Issues](https://github.com/j0k/cbhands/issues)
- **Discussions**: [GitHub Discussions](https://github.com/j0k/cbhands/discussions)

---

**cbhands v3.0.0** - The future of Battle Hands service management! 🚀
