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


def aggregate(frames_loc="frames", inputs_loc="inputs/input_recording_end_1642457354223460000.pkl", output_loc="output", loss_fns=None):
    # maps input record at near continuous FPS to the "slower" FPS of the screen recording so each frame from the screen recording has respective inputs

    assert os.path.exists(input_loc), "must specify keyboard pickle input file"
    assert os.path.exists(frames_loc), "must specify frames pickle input file"

    frames = glob.glob(f"{frames_loc}/*")
    lframes = np.zeros((len(frames), 410, 745, 3))
    lframes_ts = np.zeros((len(frames), 1))
    for n, frame in enumerate(frames):
        with open(frame, 'rb') as handle:
            b = pickle.load(handle)
            lframes[n] = b[1]
            lframes_ts[n] = b[0] 

    out = sorted(list(zip(lframes, lframes_ts)), key=lambda x: int(x[1])) # sort by frame timestamp

    
    with open(inputs_loc, "rb") as f:
        inputs = pickle.load(f)

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
    

    if loss_fns is not None:
        ll = lambda x: [round(l.eval(x), 5) for l in loss_fns]

        losses = []
        for frame, ts in out:
            frame = frame.astype(np.uint8)
            losses.append(sum(ll(frame)))
        a, b = np.array(out)[:, 0], np.array(out)[:, 1]
        total = np.asarray(list(zip(a, b, losses, act2frame)))
        # frame, timestamp, loss, actions

        # stable baselines format
        total_dict = {"acs": total[:, 3], "rews": -total[:, 2], "obs": total[:, 0], "et_rets": np.sum(-total[:, 2])}

        if not os.path.exists(output_loc):
            os.makedirs(output_loc)

        with open(f"{output_loc}/final.pkl", "wb") as f:
            pickle.dump(total_dict, f, protocol=pickle.HIGHEST_PROTOCOL)

        return total_dict
    # only observations and actions
    total_dict = {"acs": total[:, 3], "obs": total[:, 0]}

    if not os.path.exists(output_loc):
        os.makedirs(output_loc)

    with open(f"{output_loc}/final.pkl", "wb") as f:
        pickle.dump(total_dict, f, protocol=pickle.HIGHEST_PROTOCOL)
        
    

class Recorder:
    def __init__(self):
        self.inputrec = InputRecorder(
            ["a", "x", "q", "left", "right"])  # only record these keystrokes
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
    from mariogym.envs.losses import TimeLoss, LapLoss
    aggregate(loss_fns=[TimeLoss(template_directory="../../../mariokart/seven_segment_matching/time"), LapLoss(template_directory="../../../mariokart/seven_segment_matching/lap")])
    # rec = Recorder()
    # rec.start()
    # try:
    #     while True:
    #         pass
    # except KeyboardInterrupt:
    #     rec.stop()