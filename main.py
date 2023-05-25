import tkinter as tk
import os
from tkinter import ttk
import copy

def get_score(names_of_heroes):
    heroes_score = {hero: 0.0 for hero in heroes}
    for name in names_of_heroes:
        with open(f"database/{name.strip()}.txt", "r") as f:
            for line in f:
                key, value = line.strip().split(': ')[0], line.strip().split(': ')[1].split(', ')
                score, win_rate = float(value[1]), float(value[0])
                try:
                    if var.get():
                        heroes_score[key] += (win_rate + score)
                    else:
                        heroes_score[key] += score
                except:
                    pass
        for key in list(heroes_score.keys()):
            if name in key:
                del heroes_score[key]
    return heroes_score


def filter_options(event):
    text = event.widget.get().lower()
    filtered_options = [o for o in heroes if text in o.lower()]
    event.widget['values'] = filtered_options


def get_normalized_scores(output):
    output.update({k: -v for k, v in output.items()})
    max_val = max(output.values())
    min_val = min(output.values())
    for key in output:
        output[key] = round((((output[key] - min_val) / (max_val - min_val)) * 100), 2)
    return output


def get_heroes(compare):
    os.system('cls')
    combos_h = right_combos if compare else combos
    selected_heroes = [line.get() for line in combos_h if line.get()]
    selected_heroes_opposite = [line.get() for line in left_combos if line.get()] if compare else []
    output = get_score(selected_heroes)
    output_opposite = get_score(selected_heroes_opposite) if compare else {}
    output_temp = copy.deepcopy(output)
    output_opposite_temp = copy.deepcopy(output_opposite)
    if compare:
        output = get_normalized_scores(output)
        output_opposite = get_normalized_scores(output_opposite)
        del_keys = [key for key in output if not any(name in key for name in selected_heroes_opposite)]
        for key in del_keys:
            del output[key]
        del_keys = [key for key in output_opposite if not any(name in key for name in selected_heroes)]
        for key in del_keys:
            del output_opposite[key]
        output_total = round(sum(output.values()), 2)
        output_opposite_total = round(sum(output_opposite.values()), 2)
        output = dict(sorted(output.items(), key=lambda x: x[1], reverse=True))
        output_opposite = dict(sorted(output_opposite.items(), key=lambda x: x[1], reverse=True))
        print(f'Team1 points: {output_total}')
        print(f'Team2 points: {output_opposite_total}\n')
        print('Evaluation by heroes:')
        for key, value in output.items():
            print(f"{key}: {round(value, 2)}%")
        print('---------------------')
        for key, value in output_opposite.items():
            print(f"{key}: {round(value, 2)}%")
        print('---------------------')
        output_temp = get_normalized_scores(output_temp)
        output_opposite_temp = get_normalized_scores(output_opposite_temp)
        print('Best pick for Team1:')
        for key, value in sorted(output_temp.items(), key=lambda x: x[1], reverse=True)[:30]:
            print(f"{key}: {value}%")
        print('---------------------')
        print('Best pick for Team2:')
        for key, value in sorted(output_opposite_temp.items(), key=lambda x: x[1], reverse=True)[:30]:
            print(f"{key}: {value}%")
        return

    else:
        output = get_normalized_scores(output)
        for key, value in sorted(output.items(), key=lambda x: x[1], reverse=True):
            print(f"{key}: {value}%")


def compare_window():
    global left_combos, right_combos
    compare_win = tk.Toplevel(root)
    compare_win.title("Dota2Picker Compare")
    compare_win.geometry("650x180")

    left_frame = tk.Frame(compare_win)
    left_frame.pack(side="left")

    right_frame = tk.Frame(compare_win)
    right_frame.pack(side="right")

    tk.Label(compare_win, text="Team 1", fg="green", font=("Helvetica", 24)).pack(side="left")
    tk.Label(compare_win, text="Team 2", fg="red", font=("Helvetica", 24)).pack(side="right")

    left_combos = []
    for i in range(5):
        combo = ttk.Combobox(left_frame, values=heroes)
        combo.bind('<KeyRelease>', filter_options)
        combo.grid(row=i, column=0, padx=5, pady=5)
        left_combos.append(combo)

    right_combos = []
    for i in range(5):
        combo = ttk.Combobox(right_frame, values=heroes)
        combo.bind('<KeyRelease>', filter_options)
        combo.grid(row=i, column=0, padx=5, pady=5)
        right_combos.append(combo)

    bt = tk.Button(compare_win, text="Compare", command=lambda: get_heroes(True)).pack(side="bottom", fill='x')


def main():
    global combos, var, root, heroes
    root = tk.Tk()
    root.title("Dota2Picker")
    root.geometry("300x185")

    with open(f"database/Heroes.txt", "r") as f:
        heroes = [hero.strip() for hero in f.readlines()]

    combos = []
    for _ in range(5):
        combo = ttk.Combobox(root, values=heroes)
        combo.bind('<KeyRelease>', filter_options)
        combo.pack()
        combos.append(combo)

    tk.Button(root, text="Choose your heroes", command=lambda: get_heroes(False)).pack()
    tk.Button(root, text="Compare heroes", command=compare_window).pack()
    var = tk.BooleanVar()
    tk.Checkbutton(root, text='Take into account win rate? (globally)', variable=var).pack()

    root.mainloop()


if __name__ == '__main__':
    main()
