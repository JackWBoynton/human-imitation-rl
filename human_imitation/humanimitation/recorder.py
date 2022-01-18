from typing import Callable, Any, Mapping, Iterable
from inputrecord import InputRecorder
from screenrecord import ScreenRecorder

import cv2
import os
import logging
import multiprocessing
import threading
import numpy as np
import time
import pickle
import glob
import sys
from mariogym.envs.losses import TimeLoss, LapLoss

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


def aggregate(frames_loc="./frames/*", inputs_loc="inputs/input_recording_end_1642457354223460000.pkl", output_loc="output"):
    # maps input record at near continuous FPS to the "slower" FPS of the screen recording so each frame from the screen recording has respective inputs
    frames = glob.glob(frames_loc)
    print(frames)
    lframes = np.zeros((len(frames), 410, 745, 3))
    lframes_ts = np.zeros((len(frames), 1))
    for n, frame in enumerate(frames):
        with open(frame, 'rb') as handle:
            b = pickle.load(handle)
            print(b[1].shape)
            lframes[n] = b[1]
            lframes_ts[n] = b[0] 
    
    # zz = list(zip(lframes, lframes_ts))
    # first = min(zz, key=lambda x: int(x[1]))[1]
    # last = max(zz, key=lambda x: int(x[1]))[1]

    out = sorted(list(zip(lframes, lframes_ts)), key=lambda x: int(x[1]))


    with open(inputs_loc, "rb") as f:
        inputs = pickle.load(f)

    print(inputs)

    act2frame = [None]*len(frames)

    for input_ in inputs.keys():
        if len(inputs[input_]) > 0:
            for (start, stop) in inputs[input_]:
                n = 0
                for m, (frame, frame_ts) in enumerate(out):
                    if start < frame_ts and stop > frame_ts:
                        if act2frame[m] != None and input_ not in act2frame[m]: 
                            act2frame[m] = [*act2frame[m], input_]
                        else: act2frame[m] = input_
    
    

    loss = [TimeLoss(template_directory="../../../mariokart/seven_segment_matching/time"), LapLoss(template_directory="../../../mariokart/seven_segment_matching/lap")]

    ll = lambda x: [round(l.eval(x), 5) for l in loss]


    losses = []
    for frame, ts in out:
        frame = frame.astype(np.uint8)
        losses.append(sum(ll(frame)))
    a, b = np.array(out)[:, 0], np.array(out)[:, 1]
    total = np.asarray(list(zip(a, b, losses)))

    if not os.path.exists(output_loc):
        os.makedirs(output_loc)

    with open(f"{output_loc}/final.pkl", "wb") as f:
        pickle.dump(total, f, protocol=pickle.HIGHEST_PROTOCOL)

    return total
        
    
    

class Recorder:
    def __init__(self):
        self.inputrec = InputRecorder(
            ["a", "x", "q", "left", "right"])  # has own threading
        self.screenrec = ScreenRecorderThread()

    def stop(self):
        self.screenrec.stop()
        print("done join")
        self.inputrec.stop()
        aggregate(self.screenrec.sr.save_loc, self.inputrec.output)

    def start(self):
        self.inputrec.start()
        self.screenrec.start()
        print("both start")


if __name__ == "__main__":
    aggregate()
    # rec = Recorder()
    # rec.start()
    # try:
    #     while True:
    #         pass
    # except KeyboardInterrupt:
    #     rec.stop()