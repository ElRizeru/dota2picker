import tkinter as tk
import os
from tkinter import ttk
import tools

#At 05.06.2023 the code is not finished now only show team points, here is planned a full-fledged window with a table and heroes icons
def calculate_synergy(team_heroes):
    synergy_team = []
    for i in range(len(team_heroes)):
        for j in range(i + 1, len(team_heroes)):
            hero1 = team_heroes[i]
            hero2 = team_heroes[j]
            synergy = tools.get_synergy(hero1, hero2)
            if synergy is not None:
                synergy_team.append((hero1, hero2, synergy))
    return synergy_team

def calculate_counter(team1_heroes, team2_heroes):
    counter_team = []
    for hero1 in team1_heroes:
        for hero2 in team2_heroes:
            counter = tools.get_counter(hero1, hero2)
            if counter is not None:
                counter_team.append((hero1, hero2, counter))
    return counter_team

def calculating():
    try:
        team1_heroes = [combo.get() for combo in left_combos if combo.get()]
        team2_heroes = [combo.get() for combo in right_combos if combo.get()]
    except:
        pass
    
    synergy_team1_sum = sum(item[2] for item in calculate_synergy(team1_heroes))
    counter_team1_sum = sum(item[2] for item in calculate_counter(team1_heroes, team2_heroes))
    synergy_team2_sum = sum(item[2] for item in calculate_synergy(team2_heroes))
    counter_team2_sum = sum(item[2] for item in calculate_counter(team2_heroes, team1_heroes))

    if len(team1_heroes) == 0:
        print(f'Team1: 0')
        print(f'Team2: {synergy_team2_sum + counter_team2_sum}')
    elif len(team2_heroes) == 0:
        print(f'Team1: {synergy_team1_sum + counter_team1_sum}')
        print(f'Team2: 0')
    else:
        print(f'Team1: {synergy_team1_sum + counter_team1_sum}')
        print(f'Team2: {synergy_team2_sum + counter_team2_sum}')

def filter_options(event):
    text = event.widget.get().lower()
    filtered_options = [o for o in heroes if text in o.lower()]
    event.widget['values'] = filtered_options

def main():
    global left_combos, right_combos, heroes
    root = tk.Tk()
    root.title("Dota2Picker")
    root.geometry("650x300")

    heroes = sorted(tools.get_heroes_names())

    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TCombobox', foreground='black', fieldbackground='white', selectbackground='lightgray', selectforeground='black')

    left_frame = tk.Frame(root)
    right_frame = tk.Frame(root)
    left_frame.place(relx=0.05, rely=0.1, relwidth=0.4, relheight=0.8)
    right_frame.place(relx=0.55, rely=0.1, relwidth=0.4, relheight=0.8)

    tk.Label(left_frame, text="Team 1", fg="green", font=("Helvetica", 24)).pack()
    tk.Label(right_frame, text="Team 2", fg="red", font=("Helvetica", 24)).pack()

    left_combos = []
    for i in range(5):
        combo = ttk.Combobox(left_frame, values=heroes)
        combo.bind('<KeyRelease>', filter_options)
        combo.pack(padx=5, pady=5)
        left_combos.append(combo)

    right_combos = []
    for i in range(5):
        combo = ttk.Combobox(right_frame, values=heroes)
        combo.bind('<KeyRelease>', filter_options)
        combo.pack(padx=5, pady=5)
        right_combos.append(combo)

    bt = tk.Button(root, text="Compare", command=lambda: calculating())
    bt.pack(side="bottom", fill='x')

    root.mainloop()


if __name__ == '__main__':
    main()
