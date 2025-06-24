from typing import List, Dict, Tuple, Optional
from math import exp
from functools import lru_cache
from pydantic import BaseModel, confloat

class MatchupData(BaseModel):
    disadvantage: float
    winrate: confloat(ge=0, le=100)

class AnalysisLogic:
    """Core logic for calculating hero scores and team analysis."""
    def __init__(self, data_manager, k_factor: float = 0.1):
        self.dm = data_manager
        self.all_heroes = self.dm.get_hero_list()
        self.k = k_factor

    @lru_cache(maxsize=1024)
    def _calculate_base_score(self, hero_for: str, hero_against: str, use_winrate: bool) -> float:
        """Calculates advantage score with caching and winrate normalization."""
        matchup = self.dm.get_matchup_data(hero_against, hero_for)
        if not matchup:
            return 0.0

        score = matchup.disadvantage
        if use_winrate:
            winrate_modifier = 2 * (0.5 - matchup.winrate/100)
            score += winrate_modifier
        return score

    def _calculate_win_probability(self, team1_heroes: List[str], team2_heroes: List[str], use_winrate: bool) -> float:
        """Calculates estimated win probability using logistic function."""
        if not team1_heroes or not team2_heroes:
            return 50.0

        t1_advantage = sum(
            self._calculate_base_score(h1, h2, use_winrate)
            for h1 in team1_heroes for h2 in team2_heroes
        )
        t2_advantage = sum(
            self._calculate_base_score(h2, h1, use_winrate)
            for h2 in team2_heroes for h1 in team1_heroes
        )
        net_advantage = t1_advantage - t2_advantage

        probability = 1 / (1 + exp(-self.k * net_advantage))
        return probability * 100

    def get_counter_picks(self, enemy_heroes: List[str], use_winrate: bool) -> List[Tuple[str, float]]:
        """Calculates best counter-picks against enemy heroes."""
        if not enemy_heroes:
            return []
            
        potential_picks = [h for h in self.all_heroes if h not in enemy_heroes]
        scores = {}

        for pick in potential_picks:
            total_score = sum(
                self._calculate_base_score(pick, enemy, use_winrate) 
                for enemy in enemy_heroes
            )
            scores[pick] = total_score

        return sorted(scores.items(), key=lambda item: item[1], reverse=True)
        
    def analyze_teams(self, team1_heroes: List[str], team2_heroes: List[str], use_winrate: bool) -> Dict:
        """Performs full analysis of two teams with thread-safe caching."""
        t1_contributions = {
            h1: sum(self._calculate_base_score(h1, h2, use_winrate) for h2 in team2_heroes) 
            for h1 in team1_heroes
        }
        t2_contributions = {
            h2: sum(self._calculate_base_score(h2, h1, use_winrate) for h1 in team1_heroes) 
            for h2 in team2_heroes
        }

        t1_total = sum(t1_contributions.values())
        t2_total = sum(t2_contributions.values())
        win_prob = self._calculate_win_probability(team1_heroes, team2_heroes, use_winrate)
        
        picked_heroes = set(team1_heroes + team2_heroes)
        t1_suggestions = self.get_counter_picks(team2_heroes, use_winrate)
        t2_suggestions = self.get_counter_picks(team1_heroes, use_winrate)
        
        t1_suggestions = [s for s in t1_suggestions if s[0] not in picked_heroes]
        t2_suggestions = [s for s in t2_suggestions if s[0] not in picked_heroes]

        return {
            "win_probability_team1": win_prob,
            "team1_total_score": t1_total,
            "team2_total_score": t2_total,
            "team1_hero_scores": sorted(t1_contributions.items(), key=lambda x: x[1], reverse=True),
            "team2_hero_scores": sorted(t2_contributions.items(), key=lambda x: x[1], reverse=True),
            "team1_suggestions": t1_suggestions,
            "team2_suggestions": t2_suggestions
        }

    @staticmethod
    def normalize_scores(scores: List[Tuple[str, float]]) -> List[Tuple[str, float, float]]:
        """Normalizes scores to 0-100 scale for visualization."""
        if not scores:
            return []
        
        raw_scores = [s[1] for s in scores]
        min_val, max_val = min(raw_scores), max(raw_scores)

        if min_val == max_val:
            return [(name, score, 100.0) for name, score in scores]

        return [
            (name, score, ((score - min_val) / (max_val - min_val)) * 100)
            for name, score in scores
        ]