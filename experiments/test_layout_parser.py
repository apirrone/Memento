import layoutparser as lp
import cv2
from PIL import Image
import numpy as np

def preprocess(im):
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, (0, 0), fx=2, fy=2)

    # if gray.mean() > 127:
    #     thr = cv2.adaptiveThreshold(
    #         gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 57, 1.0
    #     )

    # else:
    #     thr = cv2.adaptiveThreshold(
    #         gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 57, 1.0
    #     )

    thr2=cv2.bitwise_not(gray)
    thr2 = cv2.adaptiveThreshold(thr2,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)

    thr=thr2
    cl = cv2.cvtColor(thr, cv2.COLOR_GRAY2BGR)
    return cl, thr


ocr_agent = lp.TesseractAgent("eng+fra")
im = cv2.imread("test.png")
im, thr = preprocess(im)
res = ocr_agent.detect(thr, return_response=True, agg_output_level=lp.TesseractFeatureType.BLOCK)
layout = ocr_agent.gather_data(res, agg_level=lp.TesseractFeatureType.BLOCK)
out = lp.draw_text(im, layout)
out = np.array(out)
cv2.imshow("out", out)
cv2.waitKey(0)
cv2.imwrite("out.png", out)