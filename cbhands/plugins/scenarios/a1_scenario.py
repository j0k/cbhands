"""A1 Scenario: Обычная победа - Rock vs Scissors."""

from .base_scenario import BaseScenario
from ...core import CommandResult


class A1Scenario(BaseScenario):
    """A1: Обычная победа - Player A (Rock) vs Player B (Scissors)."""
    
    @property
    def scenario_name(self) -> str:
        return "A1"
    
    @property
    def description(self) -> str:
        return "Обычная победа - Player A (Rock) vs Player B (Scissors)"
    
    def execute(self, game_verbose: bool = False, verbose_comments: bool = False) -> CommandResult:
        """Execute A1 scenario."""
        self._log_action("Starting A1 scenario: Rock vs Scissors", verbose_comments)
        
        # Check services
        services_status = self._check_services()
        if not services_status['all_running']:
            return CommandResult.error_result("Required services not available")
        
        # Start game
        if not self._start_game():
            return CommandResult.error_result("Failed to start game")
        
        self._log_action(f"Game started: {self.game_id}", verbose_comments)
        self._log_game_state(f"Player A: {self.player_a_id}, Player B: {self.player_b_id}", game_verbose)
        
        # Round 1: Rock vs Scissors
        self._log_action("Round 1: Player A chooses Rock, Player B chooses Scissors", verbose_comments)
        
        moves = [
            {"playerId": self.player_a_id, "choice": 1},  # Rock
            {"playerId": self.player_b_id, "choice": 3}   # Scissors
        ]
        
        try:
            result = self._resolve_round(moves)
            winner = self._get_winner(result)
            
            self._log_game_state(f"Round 1 result: {result}", game_verbose)
            
            if winner == "Player A":
                self._log_action("✅ SUCCESS: Player A won with Rock vs Scissors!", verbose_comments)
                return CommandResult.success_result({
                    "scenario": "1vs1.A1",
                    "description": self.description,
                    "winner": winner,
                    "table": f"test-a1-{int(time.time())}",
                    "game_id": self.game_id,
                    "execution_time": 0.001  # Placeholder
                })
            else:
                return CommandResult.error_result(f"Unexpected winner: {winner}")
                
        except Exception as e:
            return CommandResult.error_result(f"Failed to execute scenario: {str(e)}")
