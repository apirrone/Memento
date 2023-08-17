import cv2
from PIL import Image
import time
from tesserocr import PyTessBaseAPI, RIL
from pmr.utils import draw_results
import numpy as np
import pickle
from xycut import XYCut

imgs = ["0.png", "1.png", "2.png", "3.png", "4.png"]
# imgs = ["0.png"]

box = (280, 290, 1700, 560)
# with PyTessBaseAPI(psm=PSM.OSD_ONLY, oem=OEM.LSTM_ONLY) as api:
api = PyTessBaseAPI(psm=11, oem=3)

for img in imgs:
    start = time.time()
    origIm = cv2.imread(img)
    im = cv2.cvtColor(origIm, cv2.COLOR_BGR2RGB)
    im = Image.fromarray(im)
    api.SetImage(im)
    print("prepare image time", time.time() - start)
    boxes = api.GetComponentImages(RIL.TEXTLINE, True)
    print("Found {} textline image components.".format(len(boxes)))
    results = []
    bboxes = []
    for i, (im, box, _, _) in enumerate(boxes):
        api.SetRectangle(box["x"], box["y"], box["w"], box["h"])

        ocrResult = api.GetUTF8Text()
        conf = api.MeanTextConf()

        if conf < 50:
            continue

        entry = {
            "x": box["x"],
            "y": box["y"],
            "w": box["w"],
            "h": box["h"],
            "text": ocrResult,
            "conf": conf,
        }

        results.append(entry)
        bboxes.append([box["x"], box["y"], box["w"], box["h"]])
    res = []
    bboxes = np.array(bboxes)

    xycut = XYCut(bboxes, origIm.shape)
    tmp = xycut.draw_bboxes(origIm)
    a = time.time()
    xycut.cut(max_depth=2)
    print("cut time: ", time.time() - a)
    tmp = xycut.draw(tmp, 2)
    Image.fromarray(cv2.cvtColor(tmp, cv2.COLOR_BGR2RGB)).show()

    print("one image time: ", time.time() - start)
    # res = draw_results(results, origIm)
    # Image.fromarray(cv2.cvtColor(res, cv2.COLOR_BGR2RGB)).show()
    input("...")
    print("====")
