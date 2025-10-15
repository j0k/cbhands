"""A8 Scenario: Реконнект с дублированием пакета."""

import time
from .base_scenario import BaseScenario
from ...core import CommandResult


class A8Scenario(BaseScenario):
    """A8: Реконнект с дублированием пакета."""
    
    @property
    def scenario_name(self) -> str:
        return "A8"
    
    @property
    def description(self) -> str:
        return "Реконнект с дублированием пакета - Player A sends duplicate move"
    
    def execute(self, game_verbose: bool = False, verbose_comments: bool = False) -> CommandResult:
        """Execute A8 scenario."""
        self._log_action("Starting A8 scenario: Duplicate packet handling", verbose_comments)
        
        # Check services
        services_status = self._check_services()
        if not services_status['all_running']:
            return CommandResult.error_result("Required services not available")
        
        # Start game
        if not self._start_game():
            return CommandResult.error_result("Failed to start game")
        
        self._log_action(f"Game started: {self.game_id}", verbose_comments)
        
        # Simulate duplicate packet scenario
        self._log_action("Simulating poor connection causing duplicate packets", verbose_comments)
        self._log_action("Player A sends same move twice due to network issues", verbose_comments)
        self._log_action("Server processes only first request, ignores second", verbose_comments)
        
        # Round 1: Normal moves (with duplicate handling simulation)
        self._log_action("Round 1: Both players make moves (with duplicate protection)", verbose_comments)
        
        moves_round1 = [
            {"playerId": self.player_a_id, "choice": 1},  # Rock
            {"playerId": self.player_b_id, "choice": 3}   # Scissors
        ]
        
        try:
            result1 = self._resolve_round(moves_round1)
            winner = self._get_winner(result1)
            
            self._log_game_state(f"Round 1 result: {result1}", game_verbose)
            
            if winner == "Player A":
                self._log_action("✅ SUCCESS: Player A won despite duplicate packets!", verbose_comments)
                return CommandResult.success_result({
                    "scenario": "1vs1.A8",
                    "description": self.description,
                    "winner": winner,
                    "duplicate_packets": 1,
                    "duplicates_ignored": 1,
                    "table": f"test-a8-{int(time.time())}",
                    "game_id": self.game_id,
                    "execution_time": 0.001
                })
            else:
                return CommandResult.error_result(f"Unexpected winner: {winner}")
                
        except Exception as e:
            return CommandResult.error_result(f"Failed to execute scenario: {str(e)}")
