import json
import os.path


class HistoryManager:

    

    def __init__(self, user_name):
        self.user_name = user_name
        self.historyPath = self.user_name + "/" + f"{self.user_name}_history.json"
        self.current_history = self._load_user_history()


    def _load_user_history(self):
        history_file = self.historyPath
        if os.path.exists(history_file):
            with open(history_file, 'r') as file:
                history = json.load(file)
        else:
            history = {}

        return history

    def update_history(self, video_name, count=1):
        if video_name in self.current_history:
            self.current_history[video_name] += count
        else:
            self.current_history[video_name] = count

    def read_history(self):
        return self.current_history

    def save_history(self, path=None):
        history_file  = self.historyPath
        with open(history_file, 'w') as file:
            json.dump(self.current_history, file, indent=4)