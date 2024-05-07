import threading
import tkinter as tk
from tkinter import filedialog
import time
import os
import random
from moviepy.editor import VideoFileClip
import json
from data_json import DataManager, ExperimentCue
from HistoryManager import HistoryManager
import udpStreaming


NUMBER_OF_PLAYBACKS = None
data_manager = DataManager()
user_history: HistoryManager


def determine_number_of_playbacks(folder_path, number_of_videos_in_trial):
    video_files = [f for f in os.listdir(folder_path) if f.endswith(('.mp4', '.avi', '.mkv'))]
    if video_files:
        return 2 * number_of_videos_in_trial / len(video_files)
    return 0


def open_folder_explorer():
    foldername = filedialog.askdirectory(title="Select a folder", initialdir=os.getcwd())
    if foldername:
        print("Selected folder:", foldername)
        return foldername
    return None


def play_random_video(folder_path, is_cue_folder=False):
    global NUMBER_OF_PLAYBACKS
    global user_history
    played = False
    history = user_history.read_history()
    video_files = [f for f in os.listdir(folder_path) if f.endswith(('.mp4', '.avi', '.mkv'))]

    while not played:
        if video_files:
            video_filename = random.choice(video_files)
            if is_cue_folder and video_filename in history:
                if history[video_filename] >= NUMBER_OF_PLAYBACKS:
                    video_files.remove(video_filename)
                    continue
            video_path = os.path.join(folder_path, video_filename)
            print("Playing random video:", video_path)
            clip = VideoFileClip(video_path)
            clip.preview()
            if is_cue_folder:
                user_history.update_history(video_filename)
            played = True
            return video_filename
        else:
            if is_cue_folder:
                print(
                    "No new cue videos found in the selected folder. Consider resetting the user's history or selecting another folder.")
            else:
                print("No video files found in the selected folder.")

            return None
        
def play_task_video(folder_path, cue_name):
    video_files = [f for f in os.listdir(folder_path) if f.endswith(('.mp4', '.avi', '.mkv'))]
    if video_files:
        for video_filename in video_files:
            if video_filename.split("-")[0] == cue_name:
                break
        video_path = os.path.join(folder_path, video_filename)
        print("Playing task video:", video_path)
        clip = VideoFileClip(video_path)
        clip.preview()
        return video_filename
    else:
        print("No video files found in the selected folder.")
        return None


def main():
    root = tk.Tk()
    root.title("Mind-Stride Experiment")
    root.geometry("800x700")
    root.config(bg="#add8e6")

    folder_path_cross = None
    folder_path_signal = None
    folder_path_cue = None
    folder_path_task = None
    folder_path_blank = None

    def on_folder_cross_button_click():
        nonlocal folder_path_cross
        number = entry.get()
        folder_path_cross = open_folder_explorer()

    def on_folder_signal_button_click():
        nonlocal folder_path_signal
        number = entry.get()
        folder_path_signal = open_folder_explorer()

    def on_folder_cue_button_click():
        nonlocal folder_path_cue
        number = entry.get()
        folder_path_cue = open_folder_explorer()

    def on_folder_blank_button_click():
        nonlocal folder_path_blank
        number = entry.get()
        folder_path_blank = open_folder_explorer()

    def on_folder_task_button_click():
        nonlocal folder_path_task
        number = entry.get()
        folder_path_task = open_folder_explorer()

    def on_start_button_click():
        global NUMBER_OF_PLAYBACKS
        global user_history
        user_name = entry_name.get().strip()
        user_id = entry_user_id.get().strip()
        number = entry.get()
        user_history = HistoryManager(user_name + "_" + user_id)
        if user_name and folder_path_cross and folder_path_signal and folder_path_cue and folder_path_blank and number.isdigit():
            
            path = f"{user_name}_data"

            # Start UDP streaming in a separate thread
            udp_thread = threading.Thread(target=udpStreaming.listen_udp, args=("/"+user_name + "_" + user_id,user_name,user_id,)) 
            udp_thread.start()  
        
            NUMBER_OF_PLAYBACKS = determine_number_of_playbacks(folder_path_cue, int(number))
            for i in range(int(number)):
                play_random_video(folder_path_cross)
                play_random_video(folder_path_signal)
                start_time = time.time()
                video_name = play_random_video(folder_path_cue, True)
                end_time = time.time()

                data_manager.create_dataset(user_name, time_start=start_time, time_end=end_time,
                                            cue=ExperimentCue.CUE.value,
                                            activity=video_name, trial_number=i + 1)

               
                start_time = time.time()
                cue_name = video_name.split("-")[0]
                video_name = play_task_video(folder_path_task, cue_name)
                end_time = time.time()

                data_manager.create_dataset(user_name, time_start=start_time, time_end=end_time,
                                            cue=ExperimentCue.TASK.value,
                                            activity=video_name, trial_number=i + 1)
                
                play_random_video(folder_path_blank)

                history = user_history.read_history()

                if all(value >= NUMBER_OF_PLAYBACKS for value in history.values()):
                    print("All videos have been played the required number of times.")
                    break

            data_manager.to_save(folder_name=user_name + "_" + user_id, file_name="wynik-test")
            user_history.save_history(user_id)
            udpStreaming.stop_recording()
            root.destroy()
        else:
            print("Please enter your name, select folders, and number of trials first.")

    def close_program(event):
        root.destroy()

    label_name = tk.Label(root, text="Enter your name:", font=("Georgia", 16))
    label_name.pack()

    entry_name = tk.Entry(root, font=("Helvetica", 16))
    entry_name.pack()

    label_user_id = tk.Label(root, text="Enter user id:", font=("Georgia", 16))
    label_user_id.pack()

    entry_user_id = tk.Entry(root, font=("Helvetica", 16))
    entry_user_id.pack()

    label = tk.Label(root, text="Enter a number of trials:", font=("Georgia", 16))
    label.pack()

    entry = tk.Entry(root, font=("Helvetica", 16))
    entry.pack()

    folder_button = tk.Button(root, text="Select folder with videos of cross", command=on_folder_cross_button_click,
                              width=40, height=2, font=("Georgia", 18), bg="#f5c969")
    folder_button.pack(pady=12)

    folder_button = tk.Button(root, text="Select folder with videos of beep and signal",
                              command=on_folder_signal_button_click,
                              width=40, height=2, font=("Georgia", 18), bg="#f5c969")
    folder_button.pack(pady=12)

    folder_button = tk.Button(root, text="Select folder with videos of cue",
                              command=on_folder_cue_button_click,
                              width=40, height=2, font=("Georgia", 18), bg="#f5c969")
    folder_button.pack(pady=12)

    folder_button = tk.Button(root, text="Select folder with videos of task",
                                command=on_folder_task_button_click,
                                width=40, height=2, font=("Georgia", 18), bg="#f5c969")
    folder_button.pack(pady=12)

    folder_button = tk.Button(root, text="Select folder with videos of blank",
                              command=on_folder_blank_button_click,
                              width=40, height=2, font=("Georgia", 18), bg="#f5c969")
    folder_button.pack(pady=12)

    start_button = tk.Button(root, text="Start Program", command=on_start_button_click, width=30, height=2,
                             font=("Georgia", 18), bg="#f5c969")
    start_button.pack()

    root.bind('<Escape>', close_program)

    root.mainloop()


if __name__ == "__main__":
    main()
