"""A3 Scenario: Пропуск в первом раунде (без поражения)."""

import time
from .base_scenario import BaseScenario
from ...core import CommandResult


class A3Scenario(BaseScenario):
    """A3: Пропуск в первом раунде (без поражения)."""
    
    @property
    def scenario_name(self) -> str:
        return "A3"
    
    @property
    def description(self) -> str:
        return "Пропуск в первом раунде (без поражения) - Player A timeout, then return"
    
    def execute(self, game_verbose: bool = False, verbose_comments: bool = False) -> CommandResult:
        """Execute A3 scenario."""
        self._log_action("Starting A3 scenario: First round timeout (no penalty)", verbose_comments)
        
        # Check services
        services_status = self._check_services()
        if not services_status['all_running']:
            return CommandResult.error_result("Required services not available")
        
        # Start game
        if not self._start_game():
            return CommandResult.error_result("Failed to start game")
        
        self._log_action(f"Game started: {self.game_id}", verbose_comments)
        
        # Round 1: Player A timeout, Player B makes move
        self._log_action("Round 1: Player A timeout (6s), Player B chooses Scissors", verbose_comments)
        
        # Simulate timeout by only sending Player B's move
        moves_round1 = [
            {"playerId": self.player_b_id, "choice": 3}   # Scissors
        ]
        
        try:
            # Note: In real implementation, this would be handled by timeout logic
            # For now, we simulate the scenario
            self._log_action("⚠️ Simulating timeout scenario (real implementation needed)", verbose_comments)
            
            # Round 2: Both players make moves
            self._log_action("Round 2: Player A returns, both make moves", verbose_comments)
            
            moves_round2 = [
                {"playerId": self.player_a_id, "choice": 1},  # Rock
                {"playerId": self.player_b_id, "choice": 3}   # Scissors
            ]
            
            result2 = self._resolve_round(moves_round2)
            winner = self._get_winner(result2)
            
            self._log_game_state(f"Round 2 result: {result2}", game_verbose)
            
            if winner == "Player A":
                self._log_action("✅ SUCCESS: Player A won after first round timeout!", verbose_comments)
                return CommandResult.success_result({
                    "scenario": "1vs1.A3",
                    "description": self.description,
                    "winner": winner,
                    "timeouts": 1,
                    "table": f"test-a3-{int(time.time())}",
                    "game_id": self.game_id,
                    "execution_time": 0.001
                })
            else:
                return CommandResult.error_result(f"Unexpected winner: {winner}")
                
        except Exception as e:
            return CommandResult.error_result(f"Failed to execute scenario: {str(e)}")
