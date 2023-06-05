import requests
import sqlite3
import time
from tqdm import tqdm
import os

STEAM_API = 'you_api'
STEAM_URL = f'https://api.steampowered.com/IEconDOTA2_570/GetHeroes/v1?key={STEAM_API}&language=en'
#DOTA_ICONS_URL = 'https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/'
STARTZ_API = 'you_api'
STRATZ_URL = 'https://api.stratz.com/graphql'
'''
def download_hero_icons(hero_names, real_hero_name):
    if not os.path.exists('icons'):
        os.makedirs('icons')

    for hero_id, hero_name in hero_names.items():
        icon_url = f'{DOTA_ICONS_URL}{hero_name}.png'
        response = requests.get(icon_url)

        if response.status_code == 200:
            with open(f'icons/{real_hero_name[hero_id]}.png', 'wb') as f:
                f.write(response.content)
'''
def get_hero_names():
    response = requests.get(STEAM_URL)
    data = response.json()
    heroes = data['result']['heroes']
    hero_names = {hero['id']: hero['localized_name'] for hero in heroes}
    npc_hero_names = {hero['id']: hero['name'].replace('npc_dota_hero_', '') for hero in heroes}
    count = data['result']['count']
    return hero_names, npc_hero_names, count

def fetch_advantage_data(url, headers, hero_id):
    query = f'''
        {{
            heroStats {{
                heroVsHeroMatchup(heroId: {hero_id}) {{
                    advantage {{
                        vs {{
                            synergy
                            heroId1
                            heroId2
                        }}
                        with {{
                            synergy
                            heroId1
                            heroId2
                        }}
                    }}
                }}
            }}
        }}
    '''

    attempts = 3
    while attempts > 0:
        response = requests.post(url, json={'query': query}, headers=headers)
        data = response.json()
        try:
            advantage_data = data['data']['heroStats']['heroVsHeroMatchup']['advantage'][0]
            return advantage_data
        except:
            attempts -= 1
            time.sleep(1)

    return None

def collect_heroes_data(hero_names, advantage_data):
    vs_entries = advantage_data.get('vs', [])
    with_entries = advantage_data.get('with', [])
    heroes_data = []

    for vs_data in vs_entries:
        heroId1 = vs_data['heroId1']
        heroId2 = vs_data['heroId2']
        heroName1 = hero_names.get(heroId1, 'Unknown')
        heroName2 = hero_names.get(heroId2, 'Unknown')
        counter = vs_data['synergy']
        synergy = None

        for with_data in with_entries:
            if with_data['heroId2'] == heroId2:
                synergy = with_data['synergy']
                break

        heroes_data.append((heroId1, heroId2, heroName1, heroName2, counter, synergy))

    return heroes_data

def insert_heroes_data(conn, cursor, heroes_data):
    cursor.executemany('INSERT INTO heroes (heroId1, heroId2, heroName1, heroName2, counter, synergy) VALUES (?, ?, ?, ?, ?, ?)', heroes_data)

def update():
    conn = sqlite3.connect('heroes.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS heroes (
            heroId1 INTEGER,
            heroId2 INTEGER,
            heroName1 TEXT,
            heroName2 TEXT,
            counter REAL,
            synergy REAL
        )
    ''')

    hero_names, npc_hero_names, count = get_hero_names()
    #download_hero_icons(npc_hero_names, hero_names)

    headers = {'Authorization': f'Bearer {STARTZ_API}'}
    heroes_data = []

    with tqdm(total=count) as pbar:
        for hero_id in range(1, count + 1):
            advantage_data = fetch_advantage_data(STRATZ_URL, headers, hero_id)

            if advantage_data:
                heroes_data += collect_heroes_data(hero_names, advantage_data)

            pbar.update(1)

    if heroes_data:
        insert_heroes_data(conn, cursor, heroes_data)

    conn.commit()
    conn.close()

update()
