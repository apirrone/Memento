import pmr.utils as utils
import numpy as np
import cv2
import mss
import time
import asyncio

sct = mss.mss()


rec = utils.Recorder("test.mp4")

i = 0
for i in range(10):
    print(i)
    im = np.array(sct.grab(sct.monitors[1]))
    im = im[:, :, :-1]
    im = cv2.resize(im, utils.RESOLUTION)
    # if i%2 == 0:
    asyncio.run(rec.new_im(im))
    time.sleep(2)

rec.stop()
