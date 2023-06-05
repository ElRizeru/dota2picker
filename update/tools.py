import sqlite3

def print_all():
    with sqlite3.connect('heroes.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT FROM heroes')
        rows = cursor.fetchall()
    for row in rows:
        print(row)

def get_heroes_names():
    with sqlite3.connect('heroes.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT heroName1 FROM heroes')
        rows = cursor.fetchall()
    heroes_names = [row[0] for row in rows]
    return heroes_names

def get_counter(heroName1, heroName2):
    with sqlite3.connect('heroes.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT counter FROM heroes WHERE heroName1 = ? AND heroName2 = ?", (heroName1, heroName2))
        result = cursor.fetchone()
    return result[0] if result else None

def get_synergy(heroName1, heroName2):
    with sqlite3.connect('heroes.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT synergy FROM heroes WHERE heroName1 = ? AND heroName2 = ?", (heroName1, heroName2))
        result = cursor.fetchone()
    return result[0] if result else None
