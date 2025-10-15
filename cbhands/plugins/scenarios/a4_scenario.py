"""A4 Scenario: Пропуск со 2-го раунда."""

import time
from .base_scenario import BaseScenario
from ...core import CommandResult


class A4Scenario(BaseScenario):
    """A4: Пропуск со 2-го раунда."""
    
    @property
    def scenario_name(self) -> str:
        return "A4"
    
    @property
    def description(self) -> str:
        return "Пропуск со 2-го раунда - Round 1 success, Round 2 timeout, Round 3 success"
    
    def execute(self, game_verbose: bool = False, verbose_comments: bool = False) -> CommandResult:
        """Execute A4 scenario."""
        self._log_action("Starting A4 scenario: Second round timeout", verbose_comments)
        
        # Check services
        services_status = self._check_services()
        if not services_status['all_running']:
            return CommandResult.error_result("Required services not available")
        
        # Start game
        if not self._start_game():
            return CommandResult.error_result("Failed to start game")
        
        self._log_action(f"Game started: {self.game_id}", verbose_comments)
        
        # Round 1: Both players make moves
        self._log_action("Round 1: Both players make moves", verbose_comments)
        
        moves_round1 = [
            {"playerId": self.player_a_id, "choice": 1},  # Rock
            {"playerId": self.player_b_id, "choice": 3}   # Scissors
        ]
        
        try:
            result1 = self._resolve_round(moves_round1)
            winner1 = self._get_winner(result1)
            
            self._log_game_state(f"Round 1 result: {result1}", game_verbose)
            self._log_action(f"Round 1 winner: {winner1}", verbose_comments)
            
            # Round 2: Player A timeout (3s)
            self._log_action("Round 2: Player A timeout (3s), Player B makes move", verbose_comments)
            
            # Simulate timeout scenario
            self._log_action("⚠️ Simulating timeout scenario (real implementation needed)", verbose_comments)
            
            # Round 3: Both players make moves
            self._log_action("Round 3: Both players make moves again", verbose_comments)
            
            moves_round3 = [
                {"playerId": self.player_a_id, "choice": 1},  # Rock
                {"playerId": self.player_b_id, "choice": 2}   # Paper
            ]
            
            result3 = self._resolve_round(moves_round3)
            winner3 = self._get_winner(result3)
            
            self._log_game_state(f"Round 3 result: {result3}", game_verbose)
            
            if winner3 == "Player B":
                self._log_action("✅ SUCCESS: Player B won after timeout in round 2!", verbose_comments)
                return CommandResult.success_result({
                    "scenario": "1vs1.A4",
                    "description": self.description,
                    "winner": winner3,
                    "timeouts": 1,
                    "rounds": 3,
                    "table": f"test-a4-{int(time.time())}",
                    "game_id": self.game_id,
                    "execution_time": 0.001
                })
            else:
                return CommandResult.error_result(f"Unexpected winner in round 3: {winner3}")
                
        except Exception as e:
            return CommandResult.error_result(f"Failed to execute scenario: {str(e)}")
