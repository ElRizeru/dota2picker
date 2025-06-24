# File: src\gui.py
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Tuple, Callable
import threading
from functools import lru_cache

class HeroSelector(ttk.Frame):
    """Widget for selecting heroes."""
    MAX_HEROES = 5
    
    def __init__(self, parent, title, all_heroes):
        super().__init__(parent)
        self.all_heroes = all_heroes
        
        ttk.Label(self, text=title, style="Header.TLabel").pack(pady=(0, 5), anchor="w")

        search_frame = ttk.Frame(self)
        lists_frame = ttk.Frame(self)
        buttons_frame = ttk.Frame(lists_frame)
        
        search_frame.pack(fill="x", pady=(0, 5))
        lists_frame.pack(fill="both", expand=True)
        buttons_frame.grid(row=1, column=1, padx=5, sticky="ns")

        lists_frame.columnconfigure(0, weight=1)
        lists_frame.columnconfigure(2, weight=1)
        lists_frame.rowconfigure(1, weight=1)

        ttk.Label(search_frame, text="Search:").pack(side="left", padx=(0, 5))
        self.search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side="left", fill="x", expand=True)

        ttk.Label(lists_frame, text="Available").grid(row=0, column=0, sticky="w")
        self.available_list = tk.Listbox(
            lists_frame, selectmode="extended", 
            background="#323232", foreground="#f0f0f0",
            selectbackground="#005a9e", borderwidth=0, highlightthickness=0
        )
        self.available_list.grid(row=1, column=0, sticky="nsew", padx=(0, 5))

        ttk.Label(lists_frame, text="Selected").grid(row=0, column=2, sticky="w")
        self.selected_list = tk.Listbox(
            lists_frame, selectmode="extended", 
            background="#323232", foreground="#f0f0f0",
            selectbackground="#005a9e", borderwidth=0, highlightthickness=0
        )
        self.selected_list.grid(row=1, column=2, sticky="nsew", padx=(5, 0))

        ttk.Button(buttons_frame, text=">", command=self._add_hero, width=3).pack(pady=5)
        ttk.Button(buttons_frame, text="<", command=self._remove_hero, width=3).pack(pady=5)

        self.available_list.bind("<Double-Button-1>", lambda e: self._add_hero())
        self.selected_list.bind("<Double-Button-1>", lambda e: self._remove_hero())
        self.search_var.trace_add("write", lambda *a: self._update_list())
        self._update_list()

    def _update_list(self):
        search_term = self.search_var.get().lower()
        self.available_list.delete(0, "end")
        selected_heroes = set(self.get_selected_heroes())
        for hero in self.all_heroes:
            if search_term in hero.lower() and hero not in selected_heroes:
                self.available_list.insert("end", hero)

    def _add_hero(self):
        selected_indices = self.available_list.curselection()
        if not selected_indices: return

        if len(self.selected_list.get(0, "end")) + len(selected_indices) > self.MAX_HEROES:
            messagebox.showwarning("Limit Reached", f"A team cannot have more than {self.MAX_HEROES} heroes.")
            return
            
        heroes_to_add = [self.available_list.get(i) for i in selected_indices]
        for hero in heroes_to_add:
            self.selected_list.insert("end", hero)
        self._update_list()

    def _remove_hero(self):
        selected_indices = self.selected_list.curselection()
        if not selected_indices: return
        for i in reversed(selected_indices):
            self.selected_list.delete(i)
        self._update_list()

    def get_selected_heroes(self):
        return list(self.selected_list.get(0, "end"))

class Application(ttk.Frame):
    """Main application GUI with threading support."""
    def __init__(self, parent, data_manager, logic):
        super().__init__(parent, padding="10")
        self.parent = parent
        self.dm = data_manager
        self.logic = logic
        self.all_heroes = sorted(self.dm.get_hero_list())
        self._analysis_cache = {}
        self._configure_styles()
        self._create_widgets()

    def _configure_styles(self):
        style = ttk.Style(self)
        style.configure("Header.TLabel", font=('Segoe UI', 12, 'bold'))
        style.configure("Team1.Header.TLabel", font=('Segoe UI', 14, 'bold'), foreground='#6ccb5f')
        style.configure("Team2.Header.TLabel", font=('Segoe UI', 14, 'bold'), foreground='#d35d5d')
        style.configure("Win.Team1.TLabel", font=('Segoe UI', 16, 'bold'), foreground='#6ccb5f')
        style.configure("Win.Team2.TLabel", font=('Segoe UI', 16, 'bold'), foreground='#d35d5d')
        style.configure("Draw.TLabel", font=('Segoe UI', 16, 'bold'), foreground='orange')
        style.configure("Team1.Horizontal.TProgressbar", background='#6ccb5f')
        style.configure("Team2.Horizontal.TProgressbar", background='#d35d5d')

    def _create_widgets(self):
        options_frame = ttk.Frame(self)
        options_frame.pack(fill="x", pady=(0, 10))
        self.use_winrate_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Factor in hero winrates", variable=self.use_winrate_var).pack(side="left")

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        self.counter_tab = ttk.Frame(notebook, padding="10")
        notebook.add(self.counter_tab, text="Counter-Picker")
        self._create_counter_picker_tab()

        self.analysis_tab = ttk.Frame(notebook, padding="10")
        notebook.add(self.analysis_tab, text="Team Analysis")
        self._create_team_analysis_tab()

    def _create_counter_picker_tab(self):
        self.counter_tab.columnconfigure(0, weight=1)
        self.counter_selector = HeroSelector(self.counter_tab, "Select Enemy Heroes", self.all_heroes)
        self.counter_selector.pack(fill="x", pady=(0, 10), ipady=50)

        button_frame = ttk.Frame(self.counter_tab)
        button_frame.pack(pady=10)
        
        self.counter_button = ttk.Button(button_frame, text="Find Best Picks", command=self._on_find_counters)
        self.counter_button.pack(side="left", padx=5)
        
        self.counter_progress = ttk.Progressbar(
            button_frame, mode="indeterminate", length=100
        )

        self.counter_results_frame, self.counter_results_tree = self._create_results_widget(self.counter_tab)

    def _on_find_counters(self):
        enemy_heroes = self.counter_selector.get_selected_heroes()
        if not enemy_heroes:
            messagebox.showwarning("Input Required", "Please select at least one enemy hero.")
            return
        
        self.counter_button.pack_forget()
        self.counter_progress.pack(side="left", padx=5)
        self.counter_progress.start()
        
        threading.Thread(
            target=self._run_counter_analysis,
            args=(enemy_heroes, self.use_winrate_var.get()),
            daemon=True
        ).start()

    def _run_counter_analysis(self, enemy_heroes, use_winrate):
        """Threaded function for counter analysis."""
        try:
            cache_key = ("counter", tuple(enemy_heroes), use_winrate)
            if cache_key in self._analysis_cache:
                recommendations = self._analysis_cache[cache_key]
            else:
                recommendations = self.logic.get_counter_picks(enemy_heroes, use_winrate)
                self._analysis_cache[cache_key] = recommendations
            
            normalized = self.logic.normalize_scores(recommendations)
            self._update_ui_after(lambda: self._show_counter_results(normalized))
        except Exception as e:
            self._update_ui_after(lambda: messagebox.showerror("Analysis Error", str(e)))
        finally:
            self._update_ui_after(self._reset_counter_button)

    def _show_counter_results(self, results):
        if not self.counter_results_frame.winfo_ismapped():
            self.counter_results_frame.pack(fill="both", expand=True, pady=(10, 0))
        self._update_treeview(self.counter_results_tree, results, "Recommended Picks")

    def _reset_counter_button(self):
        self.counter_progress.stop()
        self.counter_progress.pack_forget()
        self.counter_button.pack(side="left", padx=5)

    def _create_team_analysis_tab(self):
        self.analysis_tab.columnconfigure(0, weight=1)
        self.analysis_tab.columnconfigure(1, weight=1)
        
        self.team1_selector = HeroSelector(self.analysis_tab, "Team 1 (Radiant)", self.all_heroes)
        self.team1_selector.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        self.team2_selector = HeroSelector(self.analysis_tab, "Team 2 (Dire)", self.all_heroes)
        self.team2_selector.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        bottom_frame = ttk.Frame(self.analysis_tab)
        bottom_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(10, 0))
        bottom_frame.columnconfigure(0, weight=1)

        button_frame = ttk.Frame(bottom_frame)
        button_frame.pack(pady=10)
        
        self.analyze_button = ttk.Button(button_frame, text="Analyze Draft", command=self._on_analyze_teams)
        self.analyze_button.pack(side="left", padx=5)
        
        self.analyze_progress = ttk.Progressbar(
            button_frame, mode="indeterminate", length=100
        )

        self.analysis_results_frame = ttk.Frame(bottom_frame)

    def _on_analyze_teams(self):
        t1_heroes = self.team1_selector.get_selected_heroes()
        t2_heroes = self.team2_selector.get_selected_heroes()

        if not t1_heroes or not t2_heroes:
            messagebox.showwarning("Input Required", "Please select at least one hero for each team.")
            return
        
        self.analyze_button.pack_forget()
        self.analyze_progress.pack(side="left", padx=5)
        self.analyze_progress.start()
        
        threading.Thread(
            target=self._run_team_analysis,
            args=(t1_heroes, t2_heroes, self.use_winrate_var.get()),
            daemon=True
        ).start()

    def _run_team_analysis(self, t1_heroes, t2_heroes, use_winrate):
        """Threaded function for team analysis."""
        try:
            cache_key = ("analysis", tuple(t1_heroes), tuple(t2_heroes), use_winrate)
            if cache_key in self._analysis_cache:
                analysis = self._analysis_cache[cache_key]
            else:
                analysis = self.logic.analyze_teams(t1_heroes, t2_heroes, use_winrate)
                self._analysis_cache[cache_key] = analysis
            
            self._update_ui_after(lambda: self._show_team_results(analysis))
        except Exception as e:
            self._update_ui_after(lambda: messagebox.showerror("Analysis Error", str(e)))
        finally:
            self._update_ui_after(self._reset_analyze_button)

    def _show_team_results(self, analysis):
        if not self.analysis_results_frame.winfo_ismapped():
            self._create_analysis_results_widgets()
            self.analysis_results_frame.pack(fill="both", expand=True, pady=(10, 0))

        win_prob_t1 = analysis['win_probability_team1']
        self.win_prob_bar['value'] = win_prob_t1
        
        if win_prob_t1 > 52:
            self.win_prob_label.config(text=f"Team 1 Advantage: {win_prob_t1:.1f}% Win Probability")
            self.win_prob_bar.configure(style="Team1.Horizontal.TProgressbar")
        elif win_prob_t1 < 48:
            self.win_prob_label.config(text=f"Team 2 Advantage: {100-win_prob_t1:.1f}% Win Probability")
            self.win_prob_bar.configure(style="Team2.Horizontal.TProgressbar")
        else:
            self.win_prob_label.config(text="Matchup is Even")
            self.win_prob_bar.configure(style="TProgressbar")

        self._update_treeview(self.t1_contrib_tree, self.logic.normalize_scores(analysis['team1_hero_scores']))
        self._update_treeview(self.t2_contrib_tree, self.logic.normalize_scores(analysis['team2_hero_scores']))
        self._update_treeview(self.t1_suggest_tree, self.logic.normalize_scores(analysis['team1_suggestions']))
        self._update_treeview(self.t2_suggest_tree, self.logic.normalize_scores(analysis['team2_suggestions']))

    def _reset_analyze_button(self):
        self.analyze_progress.stop()
        self.analyze_progress.pack_forget()
        self.analyze_button.pack(side="left", padx=5)

    def _create_analysis_results_widgets(self):
        self.analysis_results_frame.columnconfigure(0, weight=1)
        
        win_prob_frame = ttk.Frame(self.analysis_results_frame)
        win_prob_frame.pack(fill="x", pady=10)
        self.win_prob_label = ttk.Label(win_prob_frame, text="Win Probability", anchor="center")
        self.win_prob_label.pack()
        self.win_prob_bar = ttk.Progressbar(win_prob_frame, maximum=100, style="TProgressbar")
        self.win_prob_bar.pack(fill="x", pady=5)
        
        results_notebook = ttk.Notebook(self.analysis_results_frame)
        results_notebook.pack(fill="both", expand=True)

        t1_tab = ttk.Frame(results_notebook, padding=5)
        t2_tab = ttk.Frame(results_notebook, padding=5)
        results_notebook.add(t1_tab, text="Team 1 (Radiant) Analysis")
        results_notebook.add(t2_tab, text="Team 2 (Dire) Analysis")
        
        t1_notebook = ttk.Notebook(t1_tab)
        t1_notebook.pack(fill="both", expand=True)
        t1_contrib_frame, self.t1_contrib_tree = self._create_results_widget(t1_notebook)
        t1_suggest_frame, self.t1_suggest_tree = self._create_results_widget(t1_notebook)
        t1_notebook.add(t1_contrib_frame, text="Hero Contributions")
        t1_notebook.add(t1_suggest_frame, text="Draft Suggestions")
        
        t2_notebook = ttk.Notebook(t2_tab)
        t2_notebook.pack(fill="both", expand=True)
        t2_contrib_frame, self.t2_contrib_tree = self._create_results_widget(t2_notebook)
        t2_suggest_frame, self.t2_suggest_tree = self._create_results_widget(t2_notebook)
        t2_notebook.add(t2_contrib_frame, text="Hero Contributions")
        t2_notebook.add(t2_suggest_frame, text="Draft Suggestions")

    def _create_results_widget(self, parent) -> Tuple[ttk.Frame, ttk.Treeview]:
        container = ttk.Frame(parent)
        tree = ttk.Treeview(container, columns=('Hero', 'Score', 'Rating'), show='headings')
        tree.heading('Hero', text='Hero')
        tree.heading('Score', text='Score')
        tree.heading('Rating', text='Rating')
        tree.column('Hero', width=150, anchor='w')
        tree.column('Score', width=80, anchor='center')
        tree.column('Rating', width=80, anchor='center')
        
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)
        
        return container, tree

    def _update_treeview(self, tree: ttk.Treeview, data: List, placeholder: str = "No data"):
        tree.delete(*tree.get_children())
        if not data:
            tree.insert('', 'end', values=(placeholder, "", ""))
        else:
            for name, raw_score, norm_score in data:
                tree.insert('', 'end', values=(name, f"{raw_score:.2f}", f"{norm_score:.1f}%"))

    def _update_ui_after(self, func: Callable):
        """Thread-safe UI update helper."""
        self.parent.after(0, func)