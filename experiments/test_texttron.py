import cv2
from pmr.OCR import OCR
from TextTron.TextTron import TextTron
from pmr.utils import draw_results

dumm_ocr = OCR()
dumm_ocr.rf = 1

for i in range(4):
    im = cv2.imread(str(i)+".png")

    cl, thr = dumm_ocr.preprocess(im)
    TT = TextTron(cl, xThreshold=1, yThreshold=1)
    bboxes = dumm_ocr.convert_texttron_bbox_format(TT.textBBox)
    results = []
    for bbox in bboxes:
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
        results.append(entry)
    out = draw_results(results, im)
    cv2.imwrite("out"+str(i)+".png", out)
