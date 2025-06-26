from typing import List, Dict, Tuple
from math import exp
from functools import lru_cache
from itertools import combinations

class AnalysisLogic:
    """Core logic for calculating hero scores and team analysis."""
    def __init__(self, data_manager, adv_k_factor: float, synergy_k_factor: float, winrate_k_factor: float):
        self.dm = data_manager
        self.all_heroes = self.dm.get_hero_list()
        self.adv_k = adv_k_factor
        self.synergy_k = synergy_k_factor
        self.winrate_k = winrate_k_factor

    @lru_cache(maxsize=8192)
    def _calculate_base_score(self, hero_for: str, hero_against: str) -> float:
        """Calculates advantage score based on direct matchup data (hero_for vs hero_against)."""
        return self.dm.get_advantage_score(hero_for, hero_against)

    def _calculate_win_probability(self, team1_score: float, team2_score: float) -> float:
        """Calculates estimated win probability using a logistic function."""
        net_advantage = team1_score - team2_score
        probability = 1 / (1 + exp(-self.adv_k * net_advantage))
        return probability * 100

    def get_counter_picks(self, enemy_heroes: List[str], use_winrate: bool) -> List[Tuple[str, float]]:
        """Calculates best counter-picks against a list of enemy heroes."""
        if not enemy_heroes:
            return []
            
        potential_picks = [h for h in self.all_heroes if h not in enemy_heroes]
        scores = {}

        for pick in potential_picks:
            counter_score = sum(self._calculate_base_score(pick, enemy) for enemy in enemy_heroes)
            
            winrate_bonus = 0.0
            if use_winrate:
                winrate_bonus = (self.dm.get_hero_winrate(pick) - 50.0) * self.winrate_k
            
            scores[pick] = counter_score + winrate_bonus

        return sorted(scores.items(), key=lambda item: item[1], reverse=True)
        
    def _get_draft_suggestions(self, allies: List[str], enemies: List[str], use_winrate: bool, use_synergy: bool) -> List[Tuple[str, float]]:
        """Recommends heroes based on countering enemies and synergizing with allies."""
        picked_heroes = set(allies + enemies)
        potential_picks = [h for h in self.all_heroes if h not in picked_heroes]
        scores = {}

        for pick in potential_picks:
            counter_score = sum(self._calculate_base_score(pick, e) for e in enemies)
            
            synergy_score = 0.0
            if use_synergy and allies:
                synergy_score = sum(self.dm.get_synergy_score(pick, a) for a in allies)
            
            winrate_bonus = 0.0
            if use_winrate:
                winrate_bonus = (self.dm.get_hero_winrate(pick) - 50.0) * self.winrate_k
            
            scores[pick] = counter_score + (self.synergy_k * synergy_score) + winrate_bonus
        
        return sorted(scores.items(), key=lambda item: item[1], reverse=True)

    def analyze_teams(self, team1_heroes: List[str], team2_heroes: List[str], use_winrate: bool, use_synergy: bool) -> Dict:
        """Performs a full analysis of two teams."""
        t1_matchup_scores = {h1: sum(self._calculate_base_score(h1, h2) for h2 in team2_heroes) for h1 in team1_heroes}
        t2_matchup_scores = {h2: sum(self._calculate_base_score(h2, h1) for h1 in team1_heroes) for h2 in team2_heroes}

        t1_total_matchup_score = sum(t1_matchup_scores.values())
        t2_total_matchup_score = sum(t2_matchup_scores.values())
        
        t1_winrate_bonus = sum((self.dm.get_hero_winrate(h) - 50.0) * self.winrate_k for h in team1_heroes) if use_winrate else 0.0
        t2_winrate_bonus = sum((self.dm.get_hero_winrate(h) - 50.0) * self.winrate_k for h in team2_heroes) if use_winrate else 0.0

        t1_synergy_score = 0.0
        t2_synergy_score = 0.0
        if use_synergy:
            if len(team1_heroes) > 1:
                t1_synergy_score = sum(self.dm.get_synergy_score(h1, h2) for h1, h2 in combinations(team1_heroes, 2))
            if len(team2_heroes) > 1:
                t2_synergy_score = sum(self.dm.get_synergy_score(h1, h2) for h1, h2 in combinations(team2_heroes, 2))

        t1_total = t1_total_matchup_score + t1_winrate_bonus + (self.synergy_k * t1_synergy_score)
        t2_total = t2_total_matchup_score + t2_winrate_bonus + (self.synergy_k * t2_synergy_score)

        win_prob = self._calculate_win_probability(t1_total, t2_total)
        
        t1_hero_scores = {}
        synergy_per_hero_t1 = (self.synergy_k * t1_synergy_score) / len(team1_heroes) if team1_heroes and use_synergy else 0.0
        for h1 in team1_heroes:
            matchup_score = t1_matchup_scores[h1]
            winrate_b = (self.dm.get_hero_winrate(h1) - 50.0) * self.winrate_k if use_winrate else 0.0
            t1_hero_scores[h1] = matchup_score + winrate_b + synergy_per_hero_t1

        t2_hero_scores = {}
        synergy_per_hero_t2 = (self.synergy_k * t2_synergy_score) / len(team2_heroes) if team2_heroes and use_synergy else 0.0
        for h2 in team2_heroes:
            matchup_score = t2_matchup_scores[h2]
            winrate_b = (self.dm.get_hero_winrate(h2) - 50.0) * self.winrate_k if use_winrate else 0.0
            t2_hero_scores[h2] = matchup_score + winrate_b + synergy_per_hero_t2

        t1_suggestions = self._get_draft_suggestions(team1_heroes, team2_heroes, use_winrate, use_synergy)
        t2_suggestions = self._get_draft_suggestions(team2_heroes, team1_heroes, use_winrate, use_synergy)

        return {
            "win_probability_team1": win_prob,
            "team1_total_score": t1_total,
            "team2_total_score": t2_total,
            "team1_hero_scores": sorted(t1_hero_scores.items(), key=lambda x: x[1], reverse=True),
            "team2_hero_scores": sorted(t2_hero_scores.items(), key=lambda x: x[1], reverse=True),
            "team1_suggestions": t1_suggestions,
            "team2_suggestions": t2_suggestions
        }

    @staticmethod
    def normalize_scores(scores: List[Tuple[str, float]]) -> List[Tuple[str, float, float]]:
        """Normalizes scores to a 0-100 scale for visualization."""
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