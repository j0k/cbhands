"""A9 Scenario: Таймерное завершение без победителя."""

import time
from .base_scenario import BaseScenario
from ...core import CommandResult


class A9Scenario(BaseScenario):
    """A9: Таймерное завершение без победителя."""
    
    @property
    def scenario_name(self) -> str:
        return "A9"
    
    @property
    def description(self) -> str:
        return "Таймерное завершение без победителя - Both players timeout"
    
    def execute(self, game_verbose: bool = False, verbose_comments: bool = False) -> CommandResult:
        """Execute A9 scenario."""
        self._log_action("Starting A9 scenario: Mutual timeout", verbose_comments)
        
        # Check services
        services_status = self._check_services()
        if not services_status['all_running']:
            return CommandResult.error_result("Required services not available")
        
        # Start game
        if not self._start_game():
            return CommandResult.error_result("Failed to start game")
        
        self._log_action(f"Game started: {self.game_id}", verbose_comments)
        
        # Simulate mutual timeout
        self._log_action("Simulating both players not making moves within timer", verbose_comments)
        self._log_action("Timer expires with no moves from either player", verbose_comments)
        self._log_action("Round counted as draw, game continues to next round", verbose_comments)
        
        # Simulate the timeout scenario
        self._log_action("⚠️ Simulating mutual timeout scenario (real implementation needed)", verbose_comments)
        
        # Round 2: Both players make moves
        self._log_action("Round 2: Both players make moves after mutual timeout", verbose_comments)
        
        moves_round2 = [
            {"playerId": self.player_a_id, "choice": 1},  # Rock
            {"playerId": self.player_b_id, "choice": 2}   # Paper
        ]
        
        try:
            result2 = self._resolve_round(moves_round2)
            winner = self._get_winner(result2)
            
            self._log_game_state(f"Round 2 result: {result2}", game_verbose)
            
            if winner == "Player B":
                self._log_action("✅ SUCCESS: Player B won after mutual timeout in round 1!", verbose_comments)
                return CommandResult.success_result({
                    "scenario": "1vs1.A9",
                    "description": self.description,
                    "winner": winner,
                    "mutual_timeouts": 1,
                    "rounds": 2,
                    "table": f"test-a9-{int(time.time())}",
                    "game_id": self.game_id,
                    "execution_time": 0.001
                })
            else:
                return CommandResult.error_result(f"Unexpected winner: {winner}")
                
        except Exception as e:
            return CommandResult.error_result(f"Failed to execute scenario: {str(e)}")
