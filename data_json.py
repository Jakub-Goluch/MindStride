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
        # self.trial_number = 0

    def to_save(self, name, trial_data):
        with open(name, "w") as f:
            json.dump([data for data in trial_data], f, indent=4)

    def to_open(self, name):
        with open(name, 'r') as file:
            data = json.load(file)

        for item in data:
            item_dict = json.loads(item)
            print(json.dumps(item_dict, indent=4))

    def input_data(self, person: str, time_start: float, time_end: float, cue: ExperimentCue, activity: MotorImageryTask):
        return BlockData(person, time_start, time_end, cue, activity).to_json()

    def create_dataset(self, person: str, time_start: float, time_end: float, cue: ExperimentCue,
                       activity: MotorImageryTask, trial_number: int, list_of_data: list = None) -> list:
        if list_of_data is None:
            self.list_of_data = []

        list_of_data.append(self.input_data(person, time_start, time_end, cue, activity, eeg))

        return list_of_data

    def changeto_enum(self, video_name):
        if video_name.startswith("Lewa_scisk"):
            return 3
        elif video_name.startswith("Lewa"):
            return 4
        elif video_name.startswith("Prawa_scisk"):
            return 1
        elif video_name.startswith("Prawa"):
            return 2
        else:
            return 5
