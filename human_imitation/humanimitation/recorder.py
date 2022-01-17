from typing import Callable, Any, Mapping, Iterable
from inputrecord import InputRecorder
from screenrecord import ScreenRecorder

import logging
import multiprocessing
import threading
import numpy as np
import time


class ScreenRecorderThread(threading.Thread):
    def __init__(self, ):
        super().__init__(None, None, name="SR", daemon=True)

        self.sr = ScreenRecorder(save_location="frames")
        self.daemon = True
        self.running = True

    def run(self):
        while self.running:
            self.sr.record()

    def stop(self):
        self.running = False


def aggregate(input_record, screen_record, loss_fn):
    # maps input record at near continuous FPS to the "slower" FPS of the screen recording so each frame from the screen recording has respective inputs
    pass


class Recorder:
    def __init__(self):
        self.inputrec = InputRecorder(
            ["a", "x", "q", "left", "right"])  # has own threading
        self.screenrec = ScreenRecorderThread()

    def stop(self):
        self.screenrec.stop()
        print("done join")
        self.inputrec.stop()

    def start(self):
        self.inputrec.start()
        self.screenrec.start()
        print("both start")


if __name__ == "__main__":
    rec = Recorder()
    rec.start()
    time.sleep(2)
    rec.stop()