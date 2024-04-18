from random import uniform, randint
from typing import List
from enum import Enum
from dataclasses import dataclass
import json
from pprint import pprint
from dataclasses_json import dataclass_json


class MotorImageryTask(Enum):
    RIGHT_HAND_SQUEEZE = 1
    RIGHT_HAND_WAVE = 2
    LEFT_HAND_SQUEEZE = 3
    LEFT_HAND_WAVE = 4
    JAW = 5


class ExperimentCue(Enum):
    CUE = True
    TASK = False


#klasa narazie zbedna, brak polaczenia z urzadzeniem
@dataclass_json
@dataclass
class EEGSignal:
    DELTA: List[float]
    THETA: List[float]
    ALPHA: List[float]
    BETA_LOW: List[float]
    BETA_MID: List[float]
    BETA_HIGH: List[float]
    GAMMA: List[float]

    def __init__(self):
        self.DELTA = []
        self.THETA = []
        self.ALPHA = []
        self.BETA_LOW = []
        self.BETA_MID = []
        self.BETA_HIGH = []
        self.GAMMA = []


@dataclass_json
@dataclass
class BlockData:
    person: str
    time_start: float
    time_end: float
    cue: ExperimentCue
    activity: MotorImageryTask
    trial_number: int


class DataManager:
    def __init__(self):
        self.list_of_data = None

    def to_save(self, name, trial_data= None):
        if not trial_data:
            trial_data = self.list_of_data
        with open(name, "w") as f:
            json.dump([data for data in trial_data], f, indent=4)

    def to_open(self, name):
        with open(name, 'r') as file:
            data = json.load(file)

        for item in data:
            item_dict = json.loads(item)
            print(json.dumps(item_dict, indent=4))

    def input_data(self, person: str, time_start: float, time_end: float, cue: ExperimentCue, activity: MotorImageryTask, trial_number):
        return BlockData(person, time_start, time_end, cue, activity, trial_number).to_json()  #Block Data zawiera metadane, bez samego eeg

    def create_dataset(self, person: str, time_start: float, time_end: float, cue: ExperimentCue,
                       activity, trial_number: int) -> list:
        if self.list_of_data is None:
            self.list_of_data = []

        self.list_of_data.append(self.input_data(person, time_start, time_end, cue, self.changeto_enum(activity), trial_number))

        return self.list_of_data # po co returnowac to tu ??

    def changeto_enum(self, video_name):
        if video_name.startswith("Left_Squeeze"):
            return MotorImageryTask.LEFT_HAND_SQUEEZE
        elif video_name.startswith("Left"):
            return MotorImageryTask.LEFT_HAND_WAVE
        elif video_name.startswith("Right_Squeeze"):
            return MotorImageryTask.RIGHT_HAND_SQUEEZE
        elif video_name.startswith("Right"):
            return MotorImageryTask.RIGHT_HAND_WAVE
        else:
            return MotorImageryTask.JAW
