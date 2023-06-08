import cv2
import numpy as np
import os
import pyautogui
from PIL import Image
import tkinter as tk
from skimage.feature import match_template
from skimage import color, transform

icon_folder = 'icons'
icons = [Image.open(os.path.join(icon_folder, f)).convert('L') for f in os.listdir(icon_folder) if os.path.splitext(f)[1] == '.png']

def select_screen_area():
    regions_team1 = []
    regions_team2 = []
    start_x, start_y, end_x, end_y = 0, 0, 0, 0
    current_color = "green"

    def on_click(event):
        nonlocal start_x, start_y, current_color
        start_x, start_y = event.x, event.y
        canvas.delete("selection_rect")

        if event.num == 2:
            current_color = "red" if current_color == "green" else "green"

    def on_drag(event):
        nonlocal end_x, end_y
        end_x, end_y = event.x, event.y
        canvas.delete("selection_rect")
        canvas.create_rectangle(start_x, start_y, end_x, end_y, outline=current_color, tag="selection_rect")

    def on_release(event):
        nonlocal start_x, start_y, end_x, end_y, current_color

        if start_x != 0 and start_y != 0:
            x, y, width, height = min(start_x, end_x), min(start_y, end_y), abs(end_x - start_x), abs(end_y - start_y)
            region = (x, y, width, height)

            if current_color == "green" and len(regions_team1) < 5:
                regions_team1.append(region)
                if len(regions_team1) == 5:
                    current_color = "red"
            elif current_color == "red" and len(regions_team2) < 5:
                regions_team2.append(region)
                if len(regions_team2) == 5:
                    current_color = "green"

            start_x, start_y, end_x, end_y = 0, 0, 0, 0

        if event.num == 3 or (len(regions_team1) == 5 and len(regions_team2) == 5):
            root.quit()

    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.attributes('-alpha', 0.3)
    root.configure(background='grey')

    canvas = tk.Canvas(root, bg='grey', highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=tk.YES)

    canvas.bind('<Button-1>', on_click)
    canvas.bind('<B1-Motion>', on_drag)
    canvas.bind('<Button-2>', on_click)
    canvas.bind('<ButtonRelease-1>', on_release)
    canvas.bind('<Button-3>', on_release)

    root.mainloop()
    root.destroy()

    return regions_team1, regions_team2

def read_regions_from_file():
    config_file = "config.txt"

    if os.path.exists(config_file):
        with open(config_file, "r") as file:
            content = file.read()

        team1_data = content.split("Team 1 regions: [")[1].split("]")[0]
        team2_data = content.split("Team 2 regions: [")[1].split("]")[0]

        return eval(team1_data), eval(team2_data)

    return [], []

def find_image_on_screen(screenshot_gray):
    for icon_image_gray in icons:
        icon_array = np.array(icon_image_gray)
        screenshot_array = np.array(screenshot_gray)

        if icon_array.shape[0] > screenshot_array.shape[0] or icon_array.shape[1] > screenshot_array.shape[1]:
            icon_array = transform.resize(icon_array, screenshot_array.shape)

        result = match_template(screenshot_array, icon_array)
        threshold = 0.6
        loc = np.where(result >= threshold)

        if len(loc[0]) > 0:
            return icon_image_gray.filename

    return None

def main():
    regions_team1, regions_team2 = read_regions_from_file() if os.path.exists('config.txt') else select_screen_area()
    print("Team 1 regions:", regions_team1)
    print("Team 2 regions:", regions_team2)

    while regions_team1 or regions_team2:
        for region in regions_team1 + regions_team2:
            screenshot = pyautogui.screenshot(region=region)
            screenshot_gray = color.rgb2gray(np.array(screenshot))

            found_icon = find_image_on_screen(screenshot_gray)

            if found_icon:
                print(f"{found_icon}")
                if region in regions_team1:
                    regions_team1.remove(region)
                elif region in regions_team2:
                    regions_team2.remove(region)
            else:
                print("Иконка не найдена")

if __name__ == "__main__":
    main()
