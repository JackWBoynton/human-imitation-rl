import pickle
import time
import mss
import cv2
import numpy as np



class ScreenRecorder:
    def __init__(self, capture_location: dict = {'left' : 0, 'top' : 110, 'width' : 745, 'height' : 410}, save_location: str = "./") -> None:
        self.sct = mss.mss()
        self.mon = capture_location
        self.save_loc = save_location
        self.n = 0

    def record(self):
        rectime = time.time_ns()
        frame = np.array(self.sct.grab(self.mon))[:, :, [2,1,0]]
        
        out = (rectime, frame)
        with open(f"{self.save_loc}/frame_{self.n}.pickle", "wb") as f:
            pickle.dump(out, f, protocol=pickle.HIGHEST_PROTOCOL)
        self.n += 1