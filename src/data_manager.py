import json
from pathlib import Path
from typing import List, Dict, Optional

class DataManager:
    """Handles loading and accessing hero data from the JSON file."""
    def __init__(self, data_path: Path):
        self.data_path = data_path
        self._heroes: List[str] = []
        self._matchup_data: Dict[str, Dict[str, float]] = {}
        self._synergy_data: Dict[str, Dict[str, float]] = {}
        self._winrate_data: Dict[str, float] = {}
        self.load_data()

    def load_data(self) -> None:
        """Loads and validates hero data from the JSON file."""
        if not self.data_path.exists():
            raise FileNotFoundError(
                f"Data file not found at '{self.data_path}'. "
                f"Please run update_data.py first."
            )
        
        with open(self.data_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        required_keys = ["heroes", "matchup_data", "synergy_data", "winrate_data"]
        if not all(key in raw_data for key in required_keys):
            raise ValueError(f"Invalid data structure in JSON file. Missing one of: {', '.join(required_keys)}")
        
        self._heroes = sorted([h['name'] for h in raw_data["heroes"]])
        self._matchup_data = raw_data["matchup_data"]
        self._synergy_data = raw_data.get("synergy_data", {})
        self._winrate_data = raw_data.get("winrate_data", {})

    def get_hero_list(self) -> List[str]:
        """Returns a sorted list of all hero names."""
        return self._heroes
    
    def get_advantage_score(self, hero1: str, hero2: str) -> float:
        """
        Retrieves the advantage score of hero1 VS hero2.
        A positive value means hero1 has an advantage.
        """
        try:
            return self._matchup_data[hero1][hero2]
        except KeyError:
            return 0.0
            
    def get_synergy_score(self, hero1: str, hero2: str) -> float:
        """
        Retrieves the synergy score between two heroes.
        A positive value means hero1 and hero2 work well together.
        """
        if not self._synergy_data:
            return 0.0
        return self._synergy_data.get(hero1, {}).get(hero2, 0.0)

    def has_synergy_data(self) -> bool:
        """Checks if synergy data is available."""
        return bool(self._synergy_data)

    def get_hero_winrate(self, hero: str) -> float:
        """Retrieves the overall winrate for a single hero."""
        return self._winrate_data.get(hero, 50.0)