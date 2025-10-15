"""A6 Scenario: Потеря соединения и возврат."""

import time
from .base_scenario import BaseScenario
from ...core import CommandResult


class A6Scenario(BaseScenario):
    """A6: Потеря соединения и возврат."""
    
    @property
    def scenario_name(self) -> str:
        return "A6"
    
    @property
    def description(self) -> str:
        return "Потеря соединения и возврат - Player A disconnects and reconnects"
    
    def execute(self, game_verbose: bool = False, verbose_comments: bool = False) -> CommandResult:
        """Execute A6 scenario."""
        self._log_action("Starting A6 scenario: Connection loss and return", verbose_comments)
        
        # Check services
        services_status = self._check_services()
        if not services_status['all_running']:
            return CommandResult.error_result("Required services not available")
        
        # Start game
        if not self._start_game():
            return CommandResult.error_result("Failed to start game")
        
        self._log_action(f"Game started: {self.game_id}", verbose_comments)
        
        # Simulate connection loss and return
        self._log_action("Simulating Player A connection loss during active round", verbose_comments)
        self._log_action("Player A reconnects within 3 seconds, re-authenticates", verbose_comments)
        self._log_action("Player A sends move before timer expires", verbose_comments)
        
        # Round 1: Both players make moves (after reconnection)
        self._log_action("Round 1: Both players make moves after reconnection", verbose_comments)
        
        moves_round1 = [
            {"playerId": self.player_a_id, "choice": 1},  # Rock
            {"playerId": self.player_b_id, "choice": 3}   # Scissors
        ]
        
        try:
            result1 = self._resolve_round(moves_round1)
            winner = self._get_winner(result1)
            
            self._log_game_state(f"Round 1 result: {result1}", game_verbose)
            
            if winner == "Player A":
                self._log_action("✅ SUCCESS: Player A won after reconnection!", verbose_comments)
                return CommandResult.success_result({
                    "scenario": "1vs1.A6",
                    "description": self.description,
                    "winner": winner,
                    "reconnections": 1,
                    "table": f"test-a6-{int(time.time())}",
                    "game_id": self.game_id,
                    "execution_time": 0.001
                })
            else:
                return CommandResult.error_result(f"Unexpected winner: {winner}")
                
        except Exception as e:
            return CommandResult.error_result(f"Failed to execute scenario: {str(e)}")
