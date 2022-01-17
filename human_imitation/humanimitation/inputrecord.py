import pickle
import time
from typing import List, Callable, Any, Mapping
from pynput import keyboard
import collections

class InputTrack:
    def __init__(self, keys_to_watch) -> None:
        self.keys = dict.fromkeys(keys_to_watch, [])
        self.tmp = dict()

    def press(self, key):
        if key in self.keys.keys(): # if tracking
            self.tmp[key] = time.time_ns()

    def release(self, key):
        if key in self.tmp.keys(): # was pressed and have start time
            self.keys[key] = (self.tmp[key], time.time_ns())
            self.tmp.pop(key, None)


class InputRecorder:
    def __init__(self, keys_to_watch: List, output_dir: str = "inputs") -> None:
        self.tracker = InputTrack(keys_to_watch)
        self.output = output_dir
        self.listener = keyboard.Listener(on_press=self.onpress, on_release=self.onrelease)
        self.stop_ = False
    def onpress(self, key):
        self.tracker.press(key)
        if self.stop_:
            return False

    def onrelease(self, key):
        self.tracker.release(key)
        if self.stop_:
            return False

    def export(self):
        with open(f'{self.output}/input_recording_end_{time.time_ns()}.pkl', 'wb') as handle:
            pickle.dump(self.tracker.keys, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def start(self):
        self.listener.start()

    def stop(self):
        self.export()
        print("call stop listener")
        self.stop_ = True
        self.listener.stop()

    


