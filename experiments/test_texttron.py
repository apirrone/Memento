import cv2
from memento.OCR import OCR
from memento.utils import draw_results
from texttron_wrapper import TexttronWrapper
import time
from grid_seg import GridSeg

dumm_ocr = OCR()
dumm_ocr.rf = 1

for i in range(4):
    im = cv2.imread(str(i) + ".png")

    cl, thr = dumm_ocr.preprocess(im)
    ttw = TexttronWrapper(cl)
    bboxes = []
    results = []
    for bbox in ttw.bboxes:
        x1 = bbox[0]
        x2 = bbox[1]
        y1 = bbox[2]
        y2 = bbox[3]
        w = int(x2 - x1)
        h = int(y2 - y1)
        entry = {
            "x": int(x1),
            "y": int(y1),
            "w": w,
            "h": h,
            "text": "",
        }
        bboxes.append([x1, y1, w, h])
        print(entry)
        results.append(entry)
    gs = GridSeg(bboxes, 300, im.shape[:2])
    tmp = gs.draw_grid()
    cv2.imwrite("grid" + str(i) + ".png", tmp)
    regions = gs.get_regions()
    results = []
    for region in regions:
        entry = {
            "x": int(region[0]),
            "y": int(region[1]),
            "w": int(region[2]),
            "h": int(region[3]),
            "text": "",
        }
        results.append(entry)
    out = draw_results(results, im)
    cv2.imwrite("out" + str(i) + ".png", out)
