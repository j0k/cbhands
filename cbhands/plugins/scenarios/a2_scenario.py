"""A2 Scenario: Ничья → переигровка → победа."""

import time
from .base_scenario import BaseScenario
from ...core import CommandResult


class A2Scenario(BaseScenario):
    """A2: Ничья → переигровка → победа."""
    
    @property
    def scenario_name(self) -> str:
        return "A2"
    
    @property
    def description(self) -> str:
        return "Ничья → переигровка → победа - Rock vs Rock, then Rock vs Scissors"
    
    def execute(self, game_verbose: bool = False, verbose_comments: bool = False) -> CommandResult:
        """Execute A2 scenario."""
        self._log_action("Starting A2 scenario: Draw then win", verbose_comments)
        
        # Check services
        services_status = self._check_services()
        if not services_status['all_running']:
            return CommandResult.error_result("Required services not available")
        
        # Start game
        if not self._start_game():
            return CommandResult.error_result("Failed to start game")
        
        self._log_action(f"Game started: {self.game_id}", verbose_comments)
        self._log_game_state(f"Player A: {self.player_a_id}, Player B: {self.player_b_id}", game_verbose)
        
        # Round 1: Rock vs Rock (draw)
        self._log_action("Round 1: Player A chooses Rock, Player B chooses Rock (DRAW)", verbose_comments)
        
        moves_round1 = [
            {"playerId": self.player_a_id, "choice": 1},  # Rock
            {"playerId": self.player_b_id, "choice": 1}   # Rock
        ]
        
        try:
            result1 = self._resolve_round(moves_round1)
            is_draw1 = self._is_draw(result1)
            
            self._log_game_state(f"Round 1 result: {result1}", game_verbose)
            self._log_action(f"Round 1 is draw: {is_draw1}, winner_ids: {result1.get('result', {}).get('winnerIds', [])}", verbose_comments)
            
            if not is_draw1:
                return CommandResult.error_result(f"Expected draw in round 1, got: {result1}")
            
            self._log_action("✅ Round 1: Draw detected, game continues", verbose_comments)
            
            # Round 2: Rock vs Scissors (win)
            self._log_action("Round 2: Player A chooses Rock, Player B chooses Scissors", verbose_comments)
            
            moves_round2 = [
                {"playerId": self.player_a_id, "choice": 1},  # Rock
                {"playerId": self.player_b_id, "choice": 3}   # Scissors
            ]
            
            result2 = self._resolve_round(moves_round2)
            winner = self._get_winner(result2)
            
            self._log_game_state(f"Round 2 result: {result2}", game_verbose)
            
            if winner == "Player A":
                self._log_action("✅ SUCCESS: Player A won after draw in round 1!", verbose_comments)
                return CommandResult.success_result({
                    "scenario": "1vs1.A2",
                    "description": self.description,
                    "winner": winner,
                    "draws": 1,
                    "wins": 1,
                    "table": f"test-a2-{int(time.time())}",
                    "game_id": self.game_id,
                    "execution_time": 0.001  # Placeholder
                })
            else:
                return CommandResult.error_result(f"Unexpected winner in round 2: {winner}")
                
        except Exception as e:
            return CommandResult.error_result(f"Failed to execute scenario: {str(e)}")
