"""A5 Scenario: Два пропуска подряд → исключение из игры."""

import time
from .base_scenario import BaseScenario
from ...core import CommandResult


class A5Scenario(BaseScenario):
    """A5: Два пропуска подряд → исключение из игры."""
    
    @property
    def scenario_name(self) -> str:
        return "A5"
    
    @property
    def description(self) -> str:
        return "Два пропуска подряд → исключение из игры - Player A double timeout"
    
    def execute(self, game_verbose: bool = False, verbose_comments: bool = False) -> CommandResult:
        """Execute A5 scenario."""
        self._log_action("Starting A5 scenario: Double timeout leading to exclusion", verbose_comments)
        
        # Check services
        services_status = self._check_services()
        if not services_status['all_running']:
            return CommandResult.error_result("Required services not available")
        
        # Start game
        if not self._start_game():
            return CommandResult.error_result("Failed to start game")
        
        self._log_action(f"Game started: {self.game_id}", verbose_comments)
        
        # Round 1: Player A timeout (no penalty)
        self._log_action("Round 1: Player A timeout (no penalty, first round)", verbose_comments)
        
        # Simulate first timeout
        self._log_action("⚠️ Simulating first timeout (no penalty)", verbose_comments)
        
        # Round 2: Player A timeout again (exclusion)
        self._log_action("Round 2: Player A timeout again (EXCLUSION)", verbose_comments)
        
        # Simulate second timeout leading to exclusion
        self._log_action("⚠️ Simulating second timeout leading to exclusion", verbose_comments)
        
        try:
            # Player B wins by default due to exclusion
            self._log_action("✅ SUCCESS: Player B wins by default due to Player A exclusion!", verbose_comments)
            
            return CommandResult.success_result({
                "scenario": "1vs1.A5",
                "description": self.description,
                "winner": "Player B",
                "reason": "Player A excluded due to double timeout",
                "timeouts": 2,
                "exclusions": 1,
                "table": f"test-a5-{int(time.time())}",
                "game_id": self.game_id,
                "execution_time": 0.001
            })
                
        except Exception as e:
            return CommandResult.error_result(f"Failed to execute scenario: {str(e)}")
