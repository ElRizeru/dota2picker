import json
from pathlib import Path
from typing import List, Dict, Optional
from pydantic import BaseModel, ValidationError

class MatchupData(BaseModel):
    disadvantage: float
    winrate: float

class DataManager:
    """Handles hero matchup data with Pydantic validation."""
    def __init__(self, data_path: Path):
        self.data_path = data_path
        self._data = None
        self.load_data()

    def load_data(self) -> None:
        """Loads and validates hero matchup data."""
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data file not found at '{self.data_path}'")
        
        with open(self.data_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        if "heroes" not in raw_data or "matchup_data" not in raw_data:
            raise ValueError("Invalid data structure in JSON file")
        
        validated_matchups = {}
        for hero, opponents in raw_data["matchup_data"].items():
            validated_opponents = {}
            for opponent, data in opponents.items():
                try:
                    validated_data = MatchupData(**data)
                    validated_opponents[opponent] = validated_data
                except ValidationError:
                    validated_opponents[opponent] = MatchupData(
                        disadvantage=0.0, 
                        winrate=50.0
                    )
            validated_matchups[hero] = validated_opponents
        
        self._data = {
            "heroes": raw_data["heroes"],
            "matchup_data": validated_matchups
        }

    def get_hero_list(self) -> List[str]:
        """Returns sorted list of all hero names."""
        return sorted(self._data.get("heroes", []))
    
    def get_matchup_data(self, hero: str, opponent: str) -> Optional[MatchupData]:
        """Retrieves validated matchup data with fallback to defaults."""
        try:
            return self._data["matchup_data"][hero][opponent]
        except KeyError:
            return MatchupData(disadvantage=0.0, winrate=50.0)