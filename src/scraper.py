import json
import logging
import time
from pathlib import Path
from typing import List, Dict, Any
import shutil

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_URL = "https://www.dotabuff.com"
HEROES_URL = f"{BASE_URL}/heroes"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
MAX_WORKERS = 10

class Scraper:
    """Robust scraper with retry logic and incremental updates."""
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def _make_request(self, url: str) -> requests.Response:
        """Safe request with verification and timeout."""
        try:
            response = self.session.get(url, verify=True, timeout=15)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logging.error(f"Request failed: {url} - {e}")
            raise

    def get_all_heroes(self) -> List[Dict[str, str]]:
        """Fetches hero list with selector fallbacks."""
        response = self._make_request(HEROES_URL)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Multiple fallback selectors
        selectors = [
            'div[class*="hero-grid"]', 
            'div.tw-space-y-2', 
            'div.container'
        ]
        
        for selector in selectors:
            hero_container = soup.select_one(selector)
            if hero_container:
                break
        
        if not hero_container:
            raise ValueError("Hero container not found")
        
        heroes = []
        for link in hero_container.find_all('a', href=True):
            href = link['href']
            if href.startswith('/heroes/'):
                slug = href.replace('/heroes/', '')
                display_name = slug.replace('-', ' ').title()
                heroes.append({'name': display_name, 'slug': slug})
        
        return sorted(heroes, key=lambda x: x['name'])

    def _scrape_single_hero_matchups(self, hero: Dict[str, str]) -> Dict[str, Any]:
        """Scrapes matchup data with robust error handling."""
        hero_name = hero['name']
        hero_slug = hero['slug']
        url = f"{BASE_URL}/heroes/{hero_slug}/counters?date=patch_7.39"
        
        try:
            response = self._make_request(url)
            soup = BeautifulSoup(response.content, 'lxml')
            
            matchups = {}
            table = soup.find('table', class_='sortable')
            if not table:
                return {hero_name: {}}
                
            table_body = table.find('tbody')
            if not table_body:
                return {hero_name: {}}
                
            for row in table_body.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) < 5:
                    continue
                    
                opponent_name_tag = cells[1].find('a')
                disadvantage_cell = cells[2]
                winrate_cell = cells[3]
                
                if opponent_name_tag and 'data-value' in disadvantage_cell.attrs:
                    opponent_name = opponent_name_tag.text.strip()
                    try:
                        disadvantage = float(disadvantage_cell['data-value'])
                        winrate = float(winrate_cell['data-value'])
                        matchups[opponent_name] = {
                            "disadvantage": disadvantage,
                            "winrate": winrate
                        }
                    except (ValueError, TypeError):
                        continue
            return {hero_name: matchups}
        except Exception as e:
            logging.error(f"Error scraping {hero_name}: {e}")
            return {hero_name: {}}
        finally:
            time.sleep(0.5)

    def scrape_all_matchups(self, heroes: List[Dict[str, str]], existing_data: Dict = None) -> Dict[str, Any]:
        """Scrapes matchups with incremental updates."""
        all_matchups = existing_data.copy() if existing_data else {}
        
        heroes_to_scrape = [
            hero for hero in heroes 
            if hero['name'] not in all_matchups or not all_matchups[hero['name']]
        ]
        
        if not heroes_to_scrape:
            return all_matchups
            
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {
                executor.submit(self._scrape_single_hero_matchups, hero): hero 
                for hero in heroes_to_scrape
            }
            
            for future in tqdm(as_completed(futures), total=len(heroes_to_scrape), desc="Scraping Matchups"):
                hero = futures[future]
                try:
                    result = future.result()
                    all_matchups.update(result)
                except Exception as e:
                    logging.error(f"{hero['name']} failed: {e}")
        
        return all_matchups

    def save_data_to_json(self, heroes: List[Dict[str, str]], matchup_data: Dict, file_path: Path):
        """NEED FIX."""
        if file_path.exists():
            timestamp = int(time.time())
            backup_file = file_path.parent / f"hero_matchups_{timestamp}.json"
            shutil.copy(file_path, backup_file)
            logging.info(f"Created backup: {backup_file}")
        
        hero_names = [hero['name'] for hero in heroes]
        data_to_save = {"heroes": hero_names, "matchup_data": matchup_data}
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, indent=4)