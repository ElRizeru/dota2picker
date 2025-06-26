import json
import logging
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple
import requests
from tqdm import tqdm
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

STRATZ_URL = "https://api.stratz.com/graphql"

class Scraper:
    """Robust scraper for the Stratz API with retry logic."""
    def __init__(self):
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)

    def _make_graphql_request(self, query: str, headers: Dict) -> Dict:
        """Safe GraphQL request with error handling using the configured session."""
        try:
            response = self.session.post(STRATZ_URL, json={'query': query}, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            if "errors" in data:
                error_message = data["errors"][0]["message"]
                logging.error(f"GraphQL API error: {error_message}")
                raise ValueError(f"Stratz API Error: {error_message}")
            return data
        except requests.RequestException as e:
            logging.error(f"GraphQL request failed: {e}")
            if "response" in locals() and "json" in response.headers.get("Content-Type", ""):
                logging.error(f"API Response: {response.json()}")
            raise ValueError("Failed to communicate with Stratz API. Check your API key and connection.")

    def get_hero_map(self, auth_headers: Dict) -> Tuple[List[Dict[str, Any]], Dict[int, str]]:
        """Fetches the hero ID and name map from Stratz."""
        query = """
        query GetHeroMap {
            constants {
                heroes {
                    id
                    displayName
                }
            }
        }
        """
        data = self._make_graphql_request(query, auth_headers)
        heroes_list = data['data']['constants']['heroes']
        heroes = [{'id': h['id'], 'name': h['displayName']} for h in heroes_list]
        id_to_name = {h['id']: h['name'] for h in heroes}
        return sorted(heroes, key=lambda x: x['name']), id_to_name

    def _scrape_winrates(self, hero_ids: List[int], id_to_name_map: Dict[int, str], auth_headers: Dict) -> Dict[str, float]:
        """Fetches overall winrates for all heroes for the latest game version."""
        query = f"""
        {{
            heroStats {{
                winGameVersion(heroIds: {json.dumps(hero_ids)}) {{
                    heroId
                    winCount
                    matchCount
                }}
            }}
        }}
        """
        data = self._make_graphql_request(query, auth_headers)
        winrate_stats = data.get('data', {}).get('heroStats', {}).get('winGameVersion', [])
        
        winrates = {}
        for stat in winrate_stats:
            hero_name = id_to_name_map.get(stat['heroId'])
            if hero_name and stat['matchCount'] > 0:
                winrate = (stat['winCount'] / stat['matchCount']) * 100
                winrates[hero_name] = winrate
        return winrates

    def _scrape_single_hero_details(self, hero_id: int, id_to_name_map: Dict, auth_headers: Dict) -> Tuple[str, Dict, Dict]:
        """Scrapes matchup ('vs') and synergy ('with') data for a single hero."""
        query = f"""
        {{
            heroStats {{
                heroVsHeroMatchup(heroId: {hero_id}) {{
                    advantage {{
                        vs {{ synergy heroId2 }}
                        with {{ synergy heroId2 }}
                    }}
                }}
            }}
        }}
        """
        hero_name = id_to_name_map.get(hero_id)
        try:
            data = self._make_graphql_request(query, auth_headers)

            advantage_data = data.get('data', {}).get('heroStats', {}).get('heroVsHeroMatchup', {}).get('advantage', [])
            if not advantage_data:
                return hero_name, {}, {}

            vs_data, with_data = {}, {}
            for entry in advantage_data[0].get('vs', []):
                opponent_name = id_to_name_map.get(entry['heroId2'])
                if opponent_name:
                    vs_data[opponent_name] = entry['synergy']
            
            for entry in advantage_data[0].get('with', []):
                ally_name = id_to_name_map.get(entry['heroId2'])
                if ally_name:
                    with_data[ally_name] = entry['synergy']
            
            return hero_name, vs_data, with_data
        except Exception as e:
            logging.error(f"Error scraping details for {hero_name} (ID {hero_id}): {e}")
            return hero_name, {}, {}
        finally:
            time.sleep(0.1)

    def scrape_all_data(self, api_key: str) -> Dict[str, Any]:
        """Orchestrates scraping of all data (heroes, winrates, matchups, synergies) from Stratz."""
        auth_headers = {
            'Authorization': f'Bearer {api_key}',
            'User-Agent': 'STRATZ_API'
        }
        
        print("\nFetching hero map from Stratz...")
        heroes, id_to_name = self.get_hero_map(auth_headers)
        hero_ids = [h['id'] for h in heroes]
        print(f"Found {len(heroes)} heroes.")

        print("\nFetching overall hero winrates...")
        winrate_data = self._scrape_winrates(hero_ids, id_to_name, auth_headers)
        print(f"Fetched winrates for {len(winrate_data)} heroes.")

        print("\nScraping matchup and synergy data sequentially to respect API rate limits...")
        matchup_data, synergy_data = {}, {}
        
        for hero_id in tqdm(hero_ids, desc="Scraping Hero Details"):
            try:
                hero_name, vs, with_ = self._scrape_single_hero_details(hero_id, id_to_name, auth_headers)
                if hero_name:
                    matchup_data[hero_name] = vs
                    synergy_data[hero_name] = with_
            except Exception as e:
                logging.error(f"Scraping for hero ID {hero_id} failed in main loop: {e}")
        
        print("Symmetrizing synergy data...")
        final_synergies = synergy_data.copy()
        for hero1, allies in synergy_data.items():
            for hero2, synergy_val in allies.items():
                if hero2 not in final_synergies:
                    final_synergies[hero2] = {}
                if hero1 not in final_synergies[hero2]:
                    final_synergies[hero2][hero1] = synergy_val
        
        return {
            "heroes": heroes,
            "winrate_data": winrate_data,
            "matchup_data": matchup_data,
            "synergy_data": final_synergies,
        }

    def save_data_to_json(self, data: Dict[str, Any], file_path: Path):
        """Saves the scraped data to a single JSON file without creating a backup."""
        logging.info(f"Saving data to {file_path}")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)