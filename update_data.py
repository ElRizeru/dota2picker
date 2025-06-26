import time
from pathlib import Path
import json
import logging
from src.scraper import Scraper

def main():
    """Data updater using the Stratz API."""
    print("--- Dota 2 Hero Data Updater (Stratz API) ---")
    api_key = input("Enter your Stratz API Bearer Token: ")
    if not api_key:
        print("No API key provided. Aborting.")
        return

    data_dir = Path("data")
    data_file = data_dir / "hero_matchups.json"
    data_dir.mkdir(exist_ok=True)
    
    print(f"Data will be saved to: {data_file}")
    start_time = time.time()
    
    try:
        scraper = Scraper()
        
        all_data = scraper.scrape_all_data(api_key)
        
        print("\nSaving data...")
        scraper.save_data_to_json(all_data, data_file)
        
        duration = time.time() - start_time
        print("\n--- Success! ---")
        print(f"Updated data for {len(all_data.get('heroes', []))} heroes.")
        print(f"Time taken: {duration:.2f} seconds")
        
    except Exception as e:
        logging.error(f"An error occurred during the update process: {e}", exc_info=True)
        print(f"\n--- Error ---\n{e}")
        print("Update failed. Check logs for details.")

if __name__ == "__main__":
    main()