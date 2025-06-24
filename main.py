import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path
import tempfile

from src.gui import Application
from src.data_manager import DataManager
from src.analysis_logic import AnalysisLogic
from azure_theme import THEME_DATA

def main():
    """Main application entry point with safe theme loading."""
    try:
        root = tk.Tk()
        root.title("Dota 2 Picker")
        root.geometry("900x800")
        
        with tempfile.NamedTemporaryFile("w", suffix=".tcl", delete=False) as f:
            f.write(THEME_DATA)
            f.flush()
            root.tk.call("source", f.name)
        
        root.tk.call("ttk::theme::azure::LoadTheme")
        root.tk.call("ttk::theme::azure-dark::LoadTheme")
        ttk.Style().theme_use("azure-dark")

        data_file = Path("data/hero_matchups.json")
        data_manager = DataManager(data_file)
        analysis_logic = AnalysisLogic(data_manager, k_factor=0.12)
        
        app = Application(root, data_manager, analysis_logic)
        app.pack(fill="both", expand=True)

        root.mainloop()

    except Exception as e:
        error_root = tk.Tk()
        error_root.withdraw()
        messagebox.showerror("Fatal Error", f"Application failed to start:\n{str(e)}")
        error_root.destroy()

if __name__ == "__main__":
    main()