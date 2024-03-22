import tkinter as tk
from tkinter import filedialog
import os
import random
from moviepy.editor import VideoFileClip
import json


def open_folder_explorer():
    foldername = filedialog.askdirectory(title="Select a folder")
    if foldername:
        print("Selected folder:", foldername)
        return foldername
    return None


def play_random_video(folder_path, user_name):
    watch_history = read_watch_history()
    user_watched_videos = watch_history.get(user_name, [])

    video_files = [f for f in os.listdir(folder_path) if
                   f.endswith(('.mp4', '.avi', '.mkv')) and f not in user_watched_videos]

    if video_files:
        video_filename = random.choice(video_files)
        video_path = os.path.join(folder_path, video_filename)
        print("Playing random video:", video_path)

        clip = VideoFileClip(video_path)
        clip.preview()

        update_watch_history(user_name, video_filename)
    else:
        print(
            "No new video files found in the selected folder. Please select another folder or reset your watch history.")


def read_watch_history():
    try:
        with open("watch_history.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def update_watch_history(user_name, video_name):
    watch_history = read_watch_history()
    if user_name in watch_history:
        if video_name not in watch_history[user_name]:
            watch_history[user_name].append(video_name)
    else:
        watch_history[user_name] = [video_name]
    with open("watch_history.json", "w") as file:
        json.dump(watch_history, file, indent=4)


def main():
    root = tk.Tk()
    root.title("Mind-Stride Experiment")
    root.geometry("800x500")
    root.config(bg="#add8e6")

    folder_path = None

    def on_folder_button_click():
        nonlocal folder_path
        number = entry.get()
        folder_path = open_folder_explorer()

    def on_start_button_click():
        number = entry.get()
        user_name = user_name_entry.get()
        if folder_path and number.isdigit() and user_name:
            for i in range(int(number)):
                play_random_video(folder_path, user_name)  #
            root.destroy()
        else:
            print("Please select a folder, number of trials, and enter your name first.")

    def close_program(event):
        root.destroy()


    user_name_label = tk.Label(root, text="Enter your name:", font=("Georgia", 16))
    user_name_label.pack()

    user_name_entry = tk.Entry(root, font=("Helvetica", 16))
    user_name_entry.pack()

    label = tk.Label(root, text="Enter a number of trials:", font=("Georgia", 16))
    label.pack()

    entry = tk.Entry(root, font=("Helvetica", 16))
    entry.pack()

    folder_button = tk.Button(root, text="Select folder with videos", command=on_folder_button_click, width=30,
                              height=3, font=("Georgia", 18), bg="#f5c969")
    folder_button.pack(pady=70)

    start_button = tk.Button(root, text="Start Program", command=on_start_button_click, width=30, height=3,
                             font=("Georgia", 18), bg="#f5c969")
    start_button.pack()

    root.bind('<Escape>', close_program)

    root.mainloop()


if __name__ == "__main__":
    main()
