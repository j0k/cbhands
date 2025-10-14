"""Example plugin for cbhands v3.0.0."""

from cbhands.v3.core import BasePlugin, BaseCommand, CommandDefinition, OptionDefinition, OptionType, CommandResult, PluginMetadata


class ExampleCommand(BaseCommand):
    """Example command implementation."""
    
    def get_definition(self) -> CommandDefinition:
        """Get command definition."""
        return CommandDefinition(
            name="hello",
            description="Say hello with customizable message",
            handler=self.execute,
            options=[
                OptionDefinition(
                    name="name",
                    type=OptionType.STRING,
                    description="Name to greet",
                    default="World",
                    required=False,
                    help="The name to include in the greeting"
                ),
                OptionDefinition(
                    name="count",
                    type=OptionType.INTEGER,
                    description="Number of times to repeat",
                    default=1,
                    required=False,
                    help="How many times to repeat the greeting"
                ),
                OptionDefinition(
                    name="verbose",
                    type=OptionType.FLAG,
                    description="Enable verbose output",
                    default=False,
                    required=False,
                    help="Show additional information"
                )
            ],
            group="example"
        )
    
    def _execute_impl(self, ctx, **kwargs) -> CommandResult:
        """Execute the command."""
        name = kwargs.get('name', 'World')
        count = kwargs.get('count', 1)
        verbose = kwargs.get('verbose', False)
        
        if verbose:
            self.event_bus.emit('example.hello.verbose', {
                'name': name,
                'count': count
            })
        
        messages = []
        for i in range(count):
            message = f"Hello, {name}!"
            if verbose:
                message += f" (greeting #{i+1})"
            messages.append(message)
        
        result_message = "\n".join(messages)
        
        return CommandResult.success_result(
            result_message,
            data={
                'greetings': messages,
                'count': count,
                'name': name
            }
        )


class ExamplePlugin(BasePlugin):
    """Example plugin for cbhands v3.0.0."""
    
    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="example",
            version="1.0.0",
            description="Example plugin demonstrating v3.0.0 features",
            author="Battle Hands Team",
            email="team@battlehands.online",
            url="https://github.com/j0k/cbhands",
            license="MIT",
            dependencies=["click>=8.0.0"],
            python_requires=">=3.8"
        )
    
    def get_commands(self) -> list[CommandDefinition]:
        """Get command definitions."""
        return [
            CommandDefinition(
                name="hello",
                description="Say hello with customizable message",
                handler=self._create_hello_command,
                options=[
                    OptionDefinition(
                        name="name",
                        type=OptionType.STRING,
                        description="Name to greet",
                        default="World",
                        required=False,
                        help="The name to include in the greeting"
                    ),
                    OptionDefinition(
                        name="count",
                        type=OptionType.INTEGER,
                        description="Number of times to repeat",
                        default=1,
                        required=False,
                        help="How many times to repeat the greeting"
                    ),
                    OptionDefinition(
                        name="verbose",
                        type=OptionType.FLAG,
                        description="Enable verbose output",
                        default=False,
                        required=False,
                        help="Show additional information"
                    )
                ],
                group="example"
            ),
            CommandDefinition(
                name="info",
                description="Show plugin information",
                handler=self._create_info_command,
                group="example"
            )
        ]
    
    def _create_hello_command(self, ctx, **kwargs) -> CommandResult:
        """Create hello command handler."""
        name = kwargs.get('name', 'World')
        count = kwargs.get('count', 1)
        verbose = kwargs.get('verbose', False)
        
        if verbose:
            self.event_bus.emit('example.hello.verbose', {
                'name': name,
                'count': count
            })
        
        messages = []
        for i in range(count):
            message = f"Hello, {name}!"
            if verbose:
                message += f" (greeting #{i+1})"
            messages.append(message)
        
        result_message = "\n".join(messages)
        
        return CommandResult.success_result(
            result_message,
            data={
                'greetings': messages,
                'count': count,
                'name': name
            }
        )
    
    def _create_info_command(self, ctx, **kwargs) -> CommandResult:
        """Create info command handler."""
        metadata = self.get_metadata()
        
        info = {
            'name': metadata.name,
            'version': metadata.version,
            'description': metadata.description,
            'author': metadata.author,
            'email': metadata.email,
            'url': metadata.url,
            'license': metadata.license,
            'dependencies': metadata.dependencies or [],
            'python_requires': metadata.python_requires
        }
        
        return CommandResult.success_result(
            f"Plugin: {metadata.name} v{metadata.version}",
            data=info
        )
    
    def get_config_schema(self) -> dict:
        """Get configuration schema."""
        return {
            'type': 'object',
            'properties': {
                'default_name': {
                    'type': 'string',
                    'default': 'World',
                    'description': 'Default name for greetings'
                },
                'max_count': {
                    'type': 'integer',
                    'default': 10,
                    'minimum': 1,
                    'maximum': 100,
                    'description': 'Maximum number of repetitions'
                }
            }
        }
    
    def validate_config(self, config: dict) -> list[str]:
        """Validate plugin configuration."""
        errors = []
        
        if 'default_name' in config:
            if not isinstance(config['default_name'], str):
                errors.append("default_name must be a string")
        
        if 'max_count' in config:
            if not isinstance(config['max_count'], int):
                errors.append("max_count must be an integer")
            elif config['max_count'] < 1 or config['max_count'] > 100:
                errors.append("max_count must be between 1 and 100")
        
        return errors
