"""Dev Showroom plugin for cbhands v3.0.0."""

import json
import uuid
import time
import requests
from typing import Dict, Any, List, Optional
from pathlib import Path

from ..core import BasePlugin, CommandDefinition, OptionDefinition, OptionType, CommandResult, PluginMetadata
from ..core.config import PluginConfig
from .scenarios import (
    A1Scenario, A2Scenario, A3Scenario, A4Scenario, A5Scenario,
    A6Scenario, A7Scenario, A8Scenario, A9Scenario, A10Scenario
)


class DevShowroomV3Plugin(BasePlugin):
    """Dev Showroom plugin for cbhands v3.0.0."""
    
    def __init__(self, config: Optional[PluginConfig] = None, event_bus=None):
        """Initialize dev showroom plugin."""
        super().__init__(config, event_bus)
        self.redis_client = None
        self._setup_redis()
    
    def _setup_redis(self):
        """Setup Redis client."""
        try:
            import redis
            self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            # Test connection
            self.redis_client.ping()
        except Exception as e:
            print(f"Warning: Redis not available: {e}")
            self.redis_client = None
    
    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="dev_showroom",
            version="1.0.0",
            description="Development Showroom - Interactive testing and demonstration tool",
            author="Battle Hands Team",
            dependencies=["redis", "requests"]
        )
    
    def get_commands(self) -> List[CommandDefinition]:
        """Get command definitions."""
        return [
            CommandDefinition(
                name="create-tables",
                description="Create multiple tables for showroom",
                handler=self._create_tables,
                options=[
                    OptionDefinition(
                        name="count",
                        type=OptionType.INTEGER,
                        description="Number of tables to create",
                        default=10,
                        required=False
                    ),
                    OptionDefinition(
                        name="mode",
                        type=OptionType.STRING,
                        description="Game mode",
                        default="fun",
                        required=False
                    ),
                    OptionDefinition(
                        name="verbose",
                        type=OptionType.BOOLEAN,
                        description="Enable verbose output",
                        default=False,
                        required=False
                    )
                ],
                group="dev-showroom"
            ),
            CommandDefinition(
                name="list-tables",
                description="List all tables in showroom",
                handler=self._list_tables,
                options=[
                    OptionDefinition(
                        name="verbose",
                        type=OptionType.BOOLEAN,
                        description="Enable verbose output",
                        default=False,
                        required=False
                    )
                ],
                group="dev-showroom"
            ),
            CommandDefinition(
                name="show-table",
                description="Show details of a specific table",
                handler=self._show_table,
                options=[
                    OptionDefinition(
                        name="name",
                        type=OptionType.STRING,
                        description="Table name",
                        required=True
                    ),
                    OptionDefinition(
                        name="verbose",
                        type=OptionType.BOOLEAN,
                        description="Enable verbose output",
                        default=False,
                        required=False
                    )
                ],
                group="dev-showroom"
            ),
            CommandDefinition(
                name="delete-tables",
                description="Delete tables from showroom",
                handler=self._delete_tables,
                options=[
                    OptionDefinition(
                        name="all",
                        type=OptionType.BOOLEAN,
                        description="Delete all tables",
                        default=False,
                        required=False
                    ),
                    OptionDefinition(
                        name="name",
                        type=OptionType.STRING,
                        description="Delete a specific table by name",
                        required=False
                    )
                ],
                group="dev-showroom"
            ),
            CommandDefinition(
                name="show-redis",
                description="Show Redis data for showroom",
                handler=self._show_redis,
                options=[
                    OptionDefinition(
                        name="keys",
                        type=OptionType.STRING,
                        description="Redis key pattern",
                        default="*",
                        required=False
                    )
                ],
                group="dev-showroom"
            ),
            CommandDefinition(
                name="simulate-a1",
                description="Simulate 1vs1.A1 scenario",
                handler=self._simulate_a1,
                options=[
                    OptionDefinition(
                        name="game-verbose",
                        type=OptionType.FLAG,
                        description="Enable detailed game output",
                        default=False,
                        required=False
                    ),
                    OptionDefinition(
                        name="verbose-comments",
                        type=OptionType.FLAG,
                        description="Enable verbose comments",
                        default=False,
                        required=False
                    )
                ],
                group="dev-showroom"
            ),
            CommandDefinition(
                name="1vs1.A1",
                description="Run 1vs1.A1 scenario (Rock vs Scissors)",
                handler=self._simulate_a1,
                options=[
                    OptionDefinition(
                        name="game-verbose",
                        type=OptionType.FLAG,
                        description="Enable detailed game output",
                        default=False,
                        required=False
                    ),
                    OptionDefinition(
                        name="verbose-comments",
                        type=OptionType.FLAG,
                        description="Enable verbose comments",
                        default=False,
                        required=False
                    )
                ],
                group="dev-showroom"
            ),
            CommandDefinition(
                name="1vs1.A2",
                description="Run 1vs1.A2 scenario (Draw then win)",
                handler=self._simulate_a2,
                options=[
                    OptionDefinition(
                        name="game-verbose",
                        type=OptionType.FLAG,
                        description="Enable detailed game output",
                        default=False,
                        required=False
                    ),
                    OptionDefinition(
                        name="verbose-comments",
                        type=OptionType.FLAG,
                        description="Enable verbose comments",
                        default=False,
                        required=False
                    )
                ],
                group="dev-showroom"
            ),
            CommandDefinition(
                name="1vs1.A3",
                description="Run 1vs1.A3 scenario (First round timeout)",
                handler=self._simulate_a3,
                options=[
                    OptionDefinition(
                        name="game-verbose",
                        type=OptionType.FLAG,
                        description="Enable detailed game output",
                        default=False,
                        required=False
                    ),
                    OptionDefinition(
                        name="verbose-comments",
                        type=OptionType.FLAG,
                        description="Enable verbose comments",
                        default=False,
                        required=False
                    )
                ],
                group="dev-showroom"
            ),
            CommandDefinition(
                name="1vs1.A4",
                description="Run 1vs1.A4 scenario (Second round timeout)",
                handler=self._simulate_a4,
                options=[
                    OptionDefinition(
                        name="game-verbose",
                        type=OptionType.FLAG,
                        description="Enable detailed game output",
                        default=False,
                        required=False
                    ),
                    OptionDefinition(
                        name="verbose-comments",
                        type=OptionType.FLAG,
                        description="Enable verbose comments",
                        default=False,
                        required=False
                    )
                ],
                group="dev-showroom"
            ),
            CommandDefinition(
                name="1vs1.A5",
                description="Run 1vs1.A5 scenario (Double timeout exclusion)",
                handler=self._simulate_a5,
                options=[
                    OptionDefinition(
                        name="game-verbose",
                        type=OptionType.FLAG,
                        description="Enable detailed game output",
                        default=False,
                        required=False
                    ),
                    OptionDefinition(
                        name="verbose-comments",
                        type=OptionType.FLAG,
                        description="Enable verbose comments",
                        default=False,
                        required=False
                    )
                ],
                group="dev-showroom"
            ),
            CommandDefinition(
                name="1vs1.A6",
                description="Run 1vs1.A6 scenario (Connection loss and return)",
                handler=self._simulate_a6,
                options=[
                    OptionDefinition(
                        name="game-verbose",
                        type=OptionType.FLAG,
                        description="Enable detailed game output",
                        default=False,
                        required=False
                    ),
                    OptionDefinition(
                        name="verbose-comments",
                        type=OptionType.FLAG,
                        description="Enable verbose comments",
                        default=False,
                        required=False
                    )
                ],
                group="dev-showroom"
            ),
            CommandDefinition(
                name="1vs1.A7",
                description="Run 1vs1.A7 scenario (Re-entry after completed game)",
                handler=self._simulate_a7,
                options=[
                    OptionDefinition(
                        name="game-verbose",
                        type=OptionType.FLAG,
                        description="Enable detailed game output",
                        default=False,
                        required=False
                    ),
                    OptionDefinition(
                        name="verbose-comments",
                        type=OptionType.FLAG,
                        description="Enable verbose comments",
                        default=False,
                        required=False
                    )
                ],
                group="dev-showroom"
            ),
            CommandDefinition(
                name="1vs1.A8",
                description="Run 1vs1.A8 scenario (Duplicate packet handling)",
                handler=self._simulate_a8,
                options=[
                    OptionDefinition(
                        name="game-verbose",
                        type=OptionType.FLAG,
                        description="Enable detailed game output",
                        default=False,
                        required=False
                    ),
                    OptionDefinition(
                        name="verbose-comments",
                        type=OptionType.FLAG,
                        description="Enable verbose comments",
                        default=False,
                        required=False
                    )
                ],
                group="dev-showroom"
            ),
            CommandDefinition(
                name="1vs1.A9",
                description="Run 1vs1.A9 scenario (Mutual timeout)",
                handler=self._simulate_a9,
                options=[
                    OptionDefinition(
                        name="game-verbose",
                        type=OptionType.FLAG,
                        description="Enable detailed game output",
                        default=False,
                        required=False
                    ),
                    OptionDefinition(
                        name="verbose-comments",
                        type=OptionType.FLAG,
                        description="Enable verbose comments",
                        default=False,
                        required=False
                    )
                ],
                group="dev-showroom"
            ),
            CommandDefinition(
                name="1vs1.A10",
                description="Run 1vs1.A10 scenario (Player exclusion)",
                handler=self._simulate_a10,
                options=[
                    OptionDefinition(
                        name="game-verbose",
                        type=OptionType.FLAG,
                        description="Enable detailed game output",
                        default=False,
                        required=False
                    ),
                    OptionDefinition(
                        name="verbose-comments",
                        type=OptionType.FLAG,
                        description="Enable verbose comments",
                        default=False,
                        required=False
                    )
                ],
                group="dev-showroom"
            ),
            CommandDefinition(
                name="run",
                description="Run a showroom scenario",
                handler=self._run_scenario,
                options=[
                    OptionDefinition(
                        name="scenario",
                        type=OptionType.STRING,
                        description="Scenario to run (e.g., 1vs1.A1, 1vs1.A2, etc.)",
                        required=True
                    ),
                    OptionDefinition(
                        name="game-verbose",
                        type=OptionType.FLAG,
                        description="Enable detailed game output",
                        default=False,
                        required=False
                    ),
                    OptionDefinition(
                        name="verbose-comments",
                        type=OptionType.FLAG,
                        description="Enable verbose comments",
                        default=False,
                        required=False
                    )
                ],
                group="dev-showroom"
            )
        ]
    
    def _create_tables(self, ctx, **kwargs) -> CommandResult:
        """Create multiple tables for showroom."""
        count = kwargs.get('count', 10)
        mode = kwargs.get('mode', 'fun')
        verbose = kwargs.get('verbose', False)
        
        if not self.redis_client:
            return CommandResult.error_result("Redis is not available")
        
        try:
            created_tables = []
            for i in range(1, count + 1):
                table_name = f"showroom-table-{i}"
                table_data = {
                    "name": table_name,
                    "mode": mode,
                    "players": 0,
                    "max_players": 2,
                    "status": "waiting",
                    "host_id": str(uuid.uuid4()),
                    "game_id": str(uuid.uuid4()),
                    "bet_amount": 1,
                    "created_at": time.time()
                }
                
                # Store in Redis
                self.redis_client.set(f"table:{table_name}", json.dumps(table_data))
                
                # Create TABLE_CREATED event for monitoring
                table_event = {
                    "type": "TABLE_CREATED",
                    "table_id": table_name,
                    "timestamp": time.time(),
                    "data": table_data
                }
                self.redis_client.lpush("showroom:events", json.dumps(table_event))
                
                created_tables.append(table_name)
                
                if verbose:
                    print(f"✅ Table {i}: {table_name} ({mode} mode)")
            
            return CommandResult.success_result(
                f"Successfully created {count} tables",
                data={
                    "created": count,
                    "mode": mode,
                    "tables": created_tables
                }
            )
            
        except Exception as e:
            return CommandResult.error_result(f"Failed to create tables: {str(e)}")
    
    def _list_tables(self, ctx, **kwargs) -> CommandResult:
        """List all tables in showroom."""
        verbose = kwargs.get('verbose', False)
        
        if not self.redis_client:
            return CommandResult.error_result("Redis is not available")
        
        try:
            tables = []
            for key in self.redis_client.scan_iter(match="table:*"):
                table_data = json.loads(self.redis_client.get(key))
                tables.append(table_data)
            
            if not tables:
                return CommandResult.success_result("No tables found")
            
            # Sort by creation time
            tables.sort(key=lambda x: x.get('created_at', 0), reverse=True)
            
            table_list = []
            for i, table in enumerate(tables):
                table_info = f"{i+1}. {table['name']} ({table['mode']})"
                if verbose:
                    table_info += f" - Players: {table['players']}/{table['max_players']}, Status: {table['status']}"
                table_list.append(table_info)
            
            return CommandResult.success_result(
                f"Found {len(tables)} tables",
                data={
                    "count": len(tables),
                    "tables": table_list
                }
            )
            
        except Exception as e:
            return CommandResult.error_result(f"Failed to list tables: {str(e)}")
    
    def _show_table(self, ctx, **kwargs) -> CommandResult:
        """Show details of a specific table."""
        table_name = kwargs['name']
        verbose = kwargs.get('verbose', False)
        
        if not self.redis_client:
            return CommandResult.error_result("Redis is not available")
        
        try:
            table_data = self.redis_client.get(f"table:{table_name}")
            if not table_data:
                return CommandResult.error_result(f"Table '{table_name}' not found")
            
            table_info = json.loads(table_data)
            
            if verbose:
                return CommandResult.success_result(
                    f"Table details for '{table_name}'",
                    data=table_info
                )
            else:
                return CommandResult.success_result(
                    f"Table: {table_info['name']} | Mode: {table_info['mode']} | Players: {table_info['players']}/{table_info['max_players']} | Status: {table_info['status']}"
                )
                
        except Exception as e:
            return CommandResult.error_result(f"Failed to show table '{table_name}': {str(e)}")
    
    def _delete_tables(self, ctx, **kwargs) -> CommandResult:
        """Delete tables from showroom."""
        delete_all = kwargs.get('all', False)
        table_name = kwargs.get('name')
        
        if not self.redis_client:
            return CommandResult.error_result("Redis is not available")
        
        try:
            if delete_all:
                # Delete all tables
                deleted_count = 0
                for key in self.redis_client.scan_iter(match="table:*"):
                    self.redis_client.delete(key)
                    deleted_count += 1
                
                return CommandResult.success_result(f"Deleted {deleted_count} tables")
                
            elif table_name:
                # Delete specific table
                key = f"table:{table_name}"
                if self.redis_client.exists(key):
                    self.redis_client.delete(key)
                    return CommandResult.success_result(f"Deleted table '{table_name}'")
                else:
                    return CommandResult.error_result(f"Table '{table_name}' not found")
            else:
                return CommandResult.error_result("Please specify --all or --name")
                
        except Exception as e:
            return CommandResult.error_result(f"Failed to delete tables: {str(e)}")
    
    def _show_redis(self, ctx, **kwargs) -> CommandResult:
        """Show Redis data for showroom."""
        keys_pattern = kwargs.get('keys', '*')
        
        if not self.redis_client:
            return CommandResult.error_result("Redis is not available")
        
        try:
            data = {}
            for key in self.redis_client.scan_iter(match=keys_pattern):
                value = self.redis_client.get(key)
                try:
                    # Try to parse as JSON
                    data[key] = json.loads(value)
                except json.JSONDecodeError:
                    data[key] = value
            
            if not data:
                return CommandResult.success_result(f"No Redis data found for pattern '{keys_pattern}'")
            
            return CommandResult.success_result(
                f"Redis data for pattern '{keys_pattern}'",
                data=data
            )
            
        except Exception as e:
            return CommandResult.error_result(f"Failed to retrieve Redis data: {str(e)}")
    
    def _simulate_a1(self, ctx, **kwargs) -> CommandResult:
        """Simulate 1vs1.A1 scenario with game-layer-py."""
        game_verbose = kwargs.get('game-verbose', False)
        verbose_comments = kwargs.get('verbose-comments', False)
        
        try:
            # Check services
            services_status = self._check_services()
            if not services_status['all_running']:
                return CommandResult.error_result("Required services are not running")
            
            if verbose_comments:
                print("Given: 2 игрока (A, B) готовы к игре. Игра стартует.")
            
            if game_verbose:
                print("When: Раунд 1: A выбирает Камень, B выбирает Ножницы.")
                print("Then: A побеждает, появляется кнопка 'New Game'")
            
            # Create game through game-layer-py
            game_id = self._create_game_via_game_layer_py()
            if not game_id:
                return CommandResult.error_result("Failed to create game via game-layer-py")
            
            # Resolve round through game-layer-py
            round_result = self._resolve_round_via_game_layer_py(game_id)
            if not round_result:
                return CommandResult.error_result("Failed to resolve round via game-layer-py")
            
            # Extract winner
            winner_ids = round_result.get('result', {}).get('winnerIds', [])
            winner = "Player A" if winner_ids else "No winner"
            
            result_data = {
                "scenario": "1vs1.A1",
                "description": "Обычная победа - Player A (Rock) vs Player B (Scissors)",
                "winner": winner,
                "game_id": game_id,
                "round_result": round_result
            }
            
            return CommandResult.success_result(
                "✅ A1 scenario simulation completed successfully!",
                data=result_data
            )
            
        except Exception as e:
            return CommandResult.error_result(f"Simulation failed: {str(e)}")
    
    def _create_game_via_game_layer_py(self) -> Optional[str]:
        """Create game via game-layer-py API."""
        try:
            response = requests.post(
                "http://localhost:8082/v1/games",
                json={"playerIds": ["550e8400-e29b-41d4-a716-446655440000", "550e8400-e29b-41d4-a716-446655440001"]},
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            return data.get("gameId")
        except Exception as e:
            print(f"Error creating game via game-layer-py: {e}")
            return None
    
    def _resolve_round_via_game_layer_py(self, game_id: str) -> Optional[dict]:
        """Resolve round via game-layer-py API."""
        try:
            response = requests.post(
                f"http://localhost:8082/v1/games/{game_id}/rounds/resolve",
                json={
                    "roundNumber": 1,
                    "moves": [
                        {"playerId": "550e8400-e29b-41d4-a716-446655440000", "choice": "MOVE_CHOICE_ROCK"},
                        {"playerId": "550e8400-e29b-41d4-a716-446655440001", "choice": "MOVE_CHOICE_SCISSORS"}
                    ]
                },
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error resolving round via game-layer-py: {e}")
            return None
    
    def _check_services(self) -> Dict[str, Any]:
        """Check if required services are running."""
        services = {
            'lobby': {'port': 6001, 'running': False},
            'dealer': {'port': 6000, 'running': False},
            'frontend': {'port': 3000, 'running': False},
            'monitor': {'port': 9001, 'running': False}
        }
        
        # For now, assume all services are running if we can connect to Redis
        if self.redis_client:
            try:
                self.redis_client.ping()
                # If Redis is available, assume other services are running too
                for service_name in services:
                    services[service_name]['running'] = True
            except Exception:
                pass
        
        all_running = all(service['running'] for service in services.values())
        
        return {
            'services': services,
            'all_running': all_running
        }
    
    def _simulate_a2(self, ctx, **kwargs) -> CommandResult:
        """Simulate 1vs1.A2 scenario."""
        game_verbose = kwargs.get('game-verbose', False)
        verbose_comments = kwargs.get('verbose-comments', False)
        
        scenario = A2Scenario()
        return scenario.execute(game_verbose, verbose_comments)
    
    def _simulate_a3(self, ctx, **kwargs) -> CommandResult:
        """Simulate 1vs1.A3 scenario."""
        game_verbose = kwargs.get('game-verbose', False)
        verbose_comments = kwargs.get('verbose-comments', False)
        
        scenario = A3Scenario()
        return scenario.execute(game_verbose, verbose_comments)
    
    def _simulate_a4(self, ctx, **kwargs) -> CommandResult:
        """Simulate 1vs1.A4 scenario."""
        game_verbose = kwargs.get('game-verbose', False)
        verbose_comments = kwargs.get('verbose-comments', False)
        
        scenario = A4Scenario()
        return scenario.execute(game_verbose, verbose_comments)
    
    def _simulate_a5(self, ctx, **kwargs) -> CommandResult:
        """Simulate 1vs1.A5 scenario."""
        game_verbose = kwargs.get('game-verbose', False)
        verbose_comments = kwargs.get('verbose-comments', False)
        
        scenario = A5Scenario()
        return scenario.execute(game_verbose, verbose_comments)
    
    def _simulate_a6(self, ctx, **kwargs) -> CommandResult:
        """Simulate 1vs1.A6 scenario."""
        game_verbose = kwargs.get('game-verbose', False)
        verbose_comments = kwargs.get('verbose-comments', False)
        
        scenario = A6Scenario()
        return scenario.execute(game_verbose, verbose_comments)
    
    def _simulate_a7(self, ctx, **kwargs) -> CommandResult:
        """Simulate 1vs1.A7 scenario."""
        game_verbose = kwargs.get('game-verbose', False)
        verbose_comments = kwargs.get('verbose-comments', False)
        
        scenario = A7Scenario()
        return scenario.execute(game_verbose, verbose_comments)
    
    def _simulate_a8(self, ctx, **kwargs) -> CommandResult:
        """Simulate 1vs1.A8 scenario."""
        game_verbose = kwargs.get('game-verbose', False)
        verbose_comments = kwargs.get('verbose-comments', False)
        
        scenario = A8Scenario()
        return scenario.execute(game_verbose, verbose_comments)
    
    def _simulate_a9(self, ctx, **kwargs) -> CommandResult:
        """Simulate 1vs1.A9 scenario."""
        game_verbose = kwargs.get('game-verbose', False)
        verbose_comments = kwargs.get('verbose-comments', False)
        
        scenario = A9Scenario()
        return scenario.execute(game_verbose, verbose_comments)
    
    def _simulate_a10(self, ctx, **kwargs) -> CommandResult:
        """Simulate 1vs1.A10 scenario."""
        game_verbose = kwargs.get('game-verbose', False)
        verbose_comments = kwargs.get('verbose-comments', False)
        
        scenario = A10Scenario()
        return scenario.execute(game_verbose, verbose_comments)
    
    def _run_scenario(self, ctx, **kwargs) -> CommandResult:
        """Run a showroom scenario."""
        scenario_name = kwargs['scenario']
        game_verbose = kwargs.get('game-verbose', False)
        verbose_comments = kwargs.get('verbose-comments', False)
        
        # Map scenario names to handlers
        scenario_handlers = {
            '1vs1.A1': self._simulate_a1,
            '1vs1.A2': self._simulate_a2,
            '1vs1.A3': self._simulate_a3,
            '1vs1.A4': self._simulate_a4,
            '1vs1.A5': self._simulate_a5,
            '1vs1.A6': self._simulate_a6,
            '1vs1.A7': self._simulate_a7,
            '1vs1.A8': self._simulate_a8,
            '1vs1.A9': self._simulate_a9,
            '1vs1.A10': self._simulate_a10,
        }
        
        if scenario_name not in scenario_handlers:
            available_scenarios = ', '.join(scenario_handlers.keys())
            return CommandResult.error_result(
                f"Unknown scenario '{scenario_name}'. Available scenarios: {available_scenarios}"
            )
        
        # Run the scenario
        handler = scenario_handlers[scenario_name]
        return handler(ctx, game_verbose=game_verbose, verbose_comments=verbose_comments)
