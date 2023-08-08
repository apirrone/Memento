import pmr.utils as utils
import cv2
from pmr.OCR import Tesseract
import numpy as np
import mss
import time

ts = Tesseract(resize_factor=1, conf_threshold=20)
# sct = mss.mss()
# time.sleep(1)
# im = np.array(sct.grab(sct.monitors[1]))
# im = im[:, :, :-1]
# im = cv2.resize(im, utils.RESOLUTION)
# cv2.imwrite("test.png", im)
# exit()
im = cv2.imread("test.png")


start = time.time()
paragraphs = ts.process_image(im)
print("Processing time :", time.time() - start)
print("nb paragraphs", len(paragraphs))

res_im = utils.draw_results(paragraphs, im)
cv2.imwrite("out.png", res_im)
