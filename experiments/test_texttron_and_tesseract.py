from texttron_wrapper import TexttronWrapper
import cv2
from PIL import Image, ImageShow
import time
from memento.OCR import OCR
from memento.utils import draw_results
from tesserocr import PyTessBaseAPI, PSM, OEM, RIL

dumm_ocr = OCR()
dumm_ocr.rf = 1

imgs = ["0.png", "1.png", "2.png", "3.png", "4.png"]

with PyTessBaseAPI() as api:
    for img in imgs:
        start = time.time()
        im = cv2.imread(img)
        cl, thr = dumm_ocr.preprocess(im.copy())
        bboxes = TexttronWrapper(cl).bboxes
        results = []
        for box in bboxes:
            x1 = box[0]
            x2 = box[1]
            y1 = box[2]
            y2 = box[3]
            w = x2 - x1
            h = y2 - y1
            crop = cl[y1:y2, x1:x2, :]
            api.SetImage(Image.fromarray(crop))
            ocrResult = api.GetUTF8Text()
            entry = {
                "x": int(x1),
                "y": int(y1),
                "w": int(w),
                "h": int(h),
                "text": ocrResult,
            }
            results.append(entry)
            # tmp = cl[y1:y2, x1:x2, :]
            # tmp = cv2.rectangle(cl, (x1, x2), (w, h), (0, 0, 255), 2)
            # ImageShow.show(Image.fromarray(tmp))
            # print(ocrResult)
            # input("...")
        out = draw_results(results, im)
        cv2.imwrite("out" + str(img) + ".png", out)
        
        print(time.time() - start)
