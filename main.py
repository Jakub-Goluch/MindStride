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
    root.title("Number Entry and Folder Explorer")

    folder_path = None

    def on_folder_button_click():
        nonlocal folder_path
        number = entry.get()
        if number.isdigit():
            print("Entered number:", number)
            folder_path = open_folder_explorer()
        else:
            print("Please enter a valid number.")

    def on_start_button_click():
        number = entry.get()
        if folder_path and number.isdigit():
            for i in range(int(number)):
                play_random_video(folder_path)
            root.destroy()
        else:
            print("Please select a folder first.")

    def close_program(event):
        root.destroy()

    label = tk.Label(root, text="Enter a number:")
    label.pack()

    entry = tk.Entry(root)
    entry.pack()

    folder_button = tk.Button(root, text="Open Folder Explorer", command=on_folder_button_click)
    folder_button.pack()

    start_button = tk.Button(root, text="Start Program", command=on_start_button_click)
    start_button.pack()

    root.bind('<Escape>', close_program)

    root.mainloop()


if __name__ == "__main__":
    main()
