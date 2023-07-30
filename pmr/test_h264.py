import mss
import numpy as np
import cv2
import time
import asyncio
from utils import Recorder, RESOLUTION


sct = mss.mss()
recorder = Recorder("test.mp4")
recorder.start()
i = 0
s = time.time()
while True:
    i += 1
    print(i)
    im = np.array(sct.grab(sct.monitors[1]))
    im = im[:, :, :-1]
    im = cv2.resize(im, RESOLUTION)
    asyncio.run(recorder.new_im(im))

    if time.time() - s > 5:
        break
recorder.stop()
