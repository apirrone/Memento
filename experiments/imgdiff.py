import mss
import numpy as np
import time
import cv2

sct = mss.mss()

im1 = np.array(sct.grab(sct.monitors[1]))
time.sleep(1)
im2 = np.array(sct.grab(sct.monitors[1]))
cv2.imwrite("im1.png", im1)
cv2.imwrite("im2.png", im2)
start = time.time()
diff = np.bitwise_xor(im1, im2)
print(np.sum(diff) / (im1.shape[0] * im1.shape[1] * im1.shape[2]))
print("Time :", time.time() - start)
cv2.imwrite("diff.jpg", diff)   
