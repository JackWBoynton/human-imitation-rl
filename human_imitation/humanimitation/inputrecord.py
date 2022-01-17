import pickle
import time
from typing import List, Callable, Any, Mapping
from pynput import keyboard
import collections

def my_key_parse(key):
    try:
        return key.char
    except:
        return str(key).split(".")[-1]

class InputTrack:
    def __init__(self, keys_to_watch) -> None:
        self.keys = dict()
        for key in keys_to_watch:
            self.keys[key] = []
        self.tmp = dict()

    def press(self, key):
        key = my_key_parse(key)

        if key in self.keys.keys(): # if tracking
            if key not in self.tmp.keys():
                # already waiting for release -->
                self.tmp[key] = time.time_ns()

    def release(self, key):
        key = my_key_parse(key)
        if key in self.tmp.keys(): # was pressed and have start time
            self.keys[key].append((self.tmp[key], time.time_ns()))
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
        print(self.tracker.keys)
        with open(f'{self.output}/input_recording_end_{time.time_ns()}.pkl', 'wb') as handle:
            pickle.dump(self.tracker.keys, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def start(self):
        self.listener.start()

    def stop(self):
        self.export()
        print("call stop listener")
        self.stop_ = True
        self.listener.stop()

    


