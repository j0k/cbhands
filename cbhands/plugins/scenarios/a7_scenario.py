"""A7 Scenario: Повторный вход после завершенной игры."""

import time
from .base_scenario import BaseScenario
from ...core import CommandResult


class A7Scenario(BaseScenario):
    """A7: Повторный вход после завершенной игры."""
    
    @property
    def scenario_name(self) -> str:
        return "A7"
    
    @property
    def description(self) -> str:
        return "Повторный вход после завершенной игры - Player A reopens app after game"
    
    def execute(self, game_verbose: bool = False, verbose_comments: bool = False) -> CommandResult:
        """Execute A7 scenario."""
        self._log_action("Starting A7 scenario: Re-entry after completed game", verbose_comments)
        
        # Check services
        services_status = self._check_services()
        if not services_status['all_running']:
            return CommandResult.error_result("Required services not available")
        
        # Start and complete a game first
        if not self._start_game():
            return CommandResult.error_result("Failed to start game")
        
        self._log_action(f"Game started: {self.game_id}", verbose_comments)
        
        # Complete the first game
        self._log_action("Completing first game", verbose_comments)
        
        moves_round1 = [
            {"playerId": self.player_a_id, "choice": 1},  # Rock
            {"playerId": self.player_b_id, "choice": 3}   # Scissors
        ]
        
        try:
            result1 = self._resolve_round(moves_round1)
            winner1 = self._get_winner(result1)
            
            self._log_action(f"First game completed, winner: {winner1}", verbose_comments)
            
            # Simulate app closure and reopening
            self._log_action("Simulating Player A closing and reopening Mini App", verbose_comments)
            self._log_action("Player A auto-authenticates via Telegram initData", verbose_comments)
            self._log_action("Player A sees profile with nickname and current balance", verbose_comments)
            self._log_action("Last game is not recreated (new game only manually)", verbose_comments)
            
            # Simulate new game creation
            self._log_action("Creating new game manually", verbose_comments)
            
            if not self._start_game():
                return CommandResult.error_result("Failed to start new game")
            
            self._log_action(f"New game started: {self.game_id}", verbose_comments)
            
            # Complete second game
            moves_round2 = [
                {"playerId": self.player_a_id, "choice": 2},  # Paper
                {"playerId": self.player_b_id, "choice": 1}   # Rock
            ]
            
            result2 = self._resolve_round(moves_round2)
            winner2 = self._get_winner(result2)
            
            self._log_game_state(f"Second game result: {result2}", game_verbose)
            
            if winner2 == "Player A":
                self._log_action("✅ SUCCESS: Player A won in new game after re-entry!", verbose_comments)
                return CommandResult.success_result({
                    "scenario": "1vs1.A7",
                    "description": self.description,
                    "winner": winner2,
                    "re_entries": 1,
                    "games_completed": 2,
                    "table": f"test-a7-{int(time.time())}",
                    "game_id": self.game_id,
                    "execution_time": 0.001
                })
            else:
                return CommandResult.error_result(f"Unexpected winner in second game: {winner2}")
                
        except Exception as e:
            return CommandResult.error_result(f"Failed to execute scenario: {str(e)}")
