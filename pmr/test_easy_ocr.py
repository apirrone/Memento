import mss
import numpy as np
import cv2
import easyocr
import time

sct = mss.mss()


def draw(im, results):
    for result in results:
        bb = np.array(result[0])
        # text = result[1]
        # conf = result[2]
        im = cv2.rectangle(
            im,
            (int(bb[0][0]), int(bb[0][1])),
            (int(bb[2][0]), int(bb[2][1])),
            (0, 255, 0),
            2,
        )
    return im


start = time.time()
reader = easyocr.Reader(["fr", "en"], gpu=True)
print("Loading time :", time.time() - start)
# im = np.array(sct.grab(sct.monitors[1]))
# cv2.imwrite("test.png", im)
im = cv2.imread("test.png")
im = cv2.resize(im, (0, 0), fx=0.5, fy=0.5)
im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
start = time.time()
result = reader.readtext(im, batch_size=8)
print("Processing time :", time.time() - start)

im = draw(im, result)
cv2.imwrite("aze.png", im)


# for i in range(10):
