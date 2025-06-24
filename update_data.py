import time
from pathlib import Path
import json
from src.scraper import Scraper

def main():
    """Data updater with incremental scraping and backups."""
    print("--- Dota 2 Hero Matchup Updater ---")
    data_dir = Path("data")
    data_file = data_dir / "hero_matchups.json"
    data_dir.mkdir(exist_ok=True)
    
    print(f"Data will be saved to: {data_file}")
    start_time = time.time()
    
    try:
        scraper = Scraper()
        
        print("\nFetching hero list...")
        heroes = scraper.get_all_heroes()
        print(f"Found {len(heroes)} heroes")
        
        existing_data = {}
        if data_file.exists():
            print("\nLoading existing data for incremental update...")
            with open(data_file, 'r') as f:
                existing_data = json.load(f).get("matchup_data", {})
        
        print("\nScraping matchup data...")
        matchup_data = scraper.scrape_all_matchups(heroes, existing_data)
        
        print("\nSaving data...")
        scraper.save_data_to_json(heroes, matchup_data, data_file)
        
        duration = time.time() - start_time
        print("\n--- Success! ---")
        print(f"Updated data for {len(matchup_data)} heroes")
        print(f"Time taken: {duration:.2f} seconds")
        
    except Exception as e:
        print(f"\n--- Error ---\n{e}")
        print("Update failed")

if __name__ == "__main__":
    main()