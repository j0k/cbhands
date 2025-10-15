"""Base scenario class for 1vs1 scenarios."""

import uuid
import time
import requests
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

from ...core import CommandResult


class BaseScenario(ABC):
    """Base class for all 1vs1 scenarios."""
    
    def __init__(self, 
                 dealer_host: str = "localhost",
                 dealer_port: int = 8080,
                 lobby_host: str = "localhost", 
                 lobby_port: int = 8081,
                 redis_host: str = "localhost",
                 redis_port: int = 6379):
        """Initialize scenario with service endpoints."""
        self.dealer_host = dealer_host
        self.dealer_port = dealer_port
        self.lobby_host = lobby_host
        self.lobby_port = lobby_port
        self.redis_host = redis_host
        self.redis_port = redis_port
        
        self.dealer_url = f"http://{self.dealer_host}:{self.dealer_port}"
        self.lobby_url = f"https://{self.lobby_host}:{self.lobby_port}"
        
        # Game state
        self.game_id = None
        self.player_a_id = None
        self.player_b_id = None
        self.current_round = 0
        self.results = []
        
    @property
    @abstractmethod
    def scenario_name(self) -> str:
        """Scenario identifier (e.g., 'A1', 'A2')."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable scenario description."""
        pass
    
    @abstractmethod
    def execute(self, game_verbose: bool = False, verbose_comments: bool = False) -> CommandResult:
        """Execute the scenario."""
        pass
    
    def _check_services(self) -> Dict[str, bool]:
        """Check if all required services are available."""
        try:
            # Check Dealer
            dealer_response = requests.get(f"{self.dealer_url}/v1/health", timeout=5, verify=False)
            dealer_ok = dealer_response.status_code == 200
        except:
            dealer_ok = False
            
        try:
            # Check Lobby
            lobby_response = requests.get(f"{self.lobby_url}/v1/stats", timeout=5, verify=False)
            lobby_ok = lobby_response.status_code == 200
        except:
            lobby_ok = False
            
        # For now, assume services are running if we can reach them
        # In real implementation, this would be more sophisticated
        return {
            "dealer": dealer_ok,
            "lobby": lobby_ok,
            "all_running": dealer_ok  # Only require Dealer for now
        }
    
    def _start_game(self, player_a_id: str = None, player_b_id: str = None) -> bool:
        """Start a new game with two players."""
        if player_a_id is None:
            player_a_id = str(uuid.uuid4())
        if player_b_id is None:
            player_b_id = str(uuid.uuid4())
            
        self.player_a_id = player_a_id
        self.player_b_id = player_b_id
        
        payload = {
            "playerIds": [player_a_id, player_b_id]
        }
        
        try:
            response = requests.post(
                f"{self.dealer_url}/v1/games",
                json=payload,
                timeout=5,
                verify=False
            )
            response.raise_for_status()
            game_data = response.json()
            self.game_id = game_data['game']['id']
            return True
        except Exception as e:
            print(f"Error starting game: {e}")
            return False
    
    def _resolve_round(self, moves: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Resolve a round with given moves."""
        if not self.game_id:
            raise ValueError("No active game")
            
        self.current_round += 1
        
        payload = {
            "gameId": self.game_id,
            "roundNumber": self.current_round,
            "moves": moves
        }
        
        try:
            response = requests.post(
                f"{self.dealer_url}/v1/games/{self.game_id}/rounds:resolve",
                json=payload,
                timeout=5,
                verify=False
            )
            response.raise_for_status()
            result = response.json()
            self.results.append(result)
            return result
        except Exception as e:
            print(f"Error resolving round: {e}")
            raise
    
    def _get_winner(self, result: Dict[str, Any]) -> Optional[str]:
        """Extract winner from round result."""
        winner_ids = result.get('result', {}).get('winnerIds', [])
        if self.player_a_id in winner_ids:
            return "Player A"
        elif self.player_b_id in winner_ids:
            return "Player B"
        else:
            return None
    
    def _is_draw(self, result: Dict[str, Any]) -> bool:
        """Check if round was a draw."""
        result_type = result.get('result', {}).get('resultType', '')
        return result_type == 'ROUND_RESULT_TYPE_DRAW'
    
    def _log_action(self, action: str, verbose_comments: bool = False):
        """Log an action if verbose comments are enabled."""
        if verbose_comments:
            print(f"  📝 {action}")
    
    def _log_game_state(self, state: str, game_verbose: bool = False):
        """Log game state if verbose output is enabled."""
        if game_verbose:
            print(f"  🎮 {state}")
