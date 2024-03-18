import tkinter as tk
from tkinter import filedialog
import os
import random
from moviepy.editor import VideoFileClip


def open_folder_explorer():
    foldername = filedialog.askdirectory(title="Select a folder")
    if foldername:
        print("Selected folder:", foldername)
        return foldername
    return None


def play_random_video(folder_path):
    video_files = [f for f in os.listdir(folder_path) if f.endswith(('.mp4', '.avi', '.mkv'))]
    if video_files:
        video_filename = random.choice(video_files)
        video_path = os.path.join(folder_path, video_filename)
        print("Playing random video:", video_path)
        clip = VideoFileClip(video_path)
        clip.preview()
    else:
        print("No video files found in the selected folder.")


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
        if folder_path and number.isdigit():
            for i in range(int(number)):
                play_random_video(folder_path)
            root.destroy()
        else:
            print("Please select a folder and number of trials first.")

    def close_program(event):
        root.destroy()

    label = tk.Label(root, text="Enter a number of trials:", font=("Georgia", 16))
    label.pack()

    entry = tk.Entry(root, font=("Helvetica", 16))
    entry.pack()

    folder_button = tk.Button(root, text="Select folder with videos", command=on_folder_button_click, width=30, height=3, font=("Georgia", 18), bg="#f5c969")
    folder_button.pack(pady=70)

    start_button = tk.Button(root, text="Start Program", command=on_start_button_click, width=30, height=3, font=("Georgia", 18), bg="#f5c969")
    start_button.pack()

    root.bind('<Escape>', close_program)

    root.mainloop()


if __name__ == "__main__":
    main()
