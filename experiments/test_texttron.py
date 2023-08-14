import cv2
from pmr.OCR import OCR
from pmr.utils import draw_results
from texttron_wrapper import TexttronWrapper
import time

dumm_ocr = OCR()
dumm_ocr.rf = 1

for i in range(4):
    im = cv2.imread(str(i) + ".png")

    cl, thr = dumm_ocr.preprocess(im)
    ttw = TexttronWrapper(cl)

    results = []
    for bbox in ttw.bboxes:
        x1 = bbox[0]
        x2 = bbox[1]
        y1 = bbox[2]
        y2 = bbox[3]
        entry = {
            "x": int(x1),
            "y": int(y1),
            "w": int(x2 - x1),
            "h": int(y2 - y1),
            "text": "",
        }
        print(entry)
        results.append(entry)
    out = draw_results(results, im)
    cv2.imwrite("out" + str(i) + ".png", out)
