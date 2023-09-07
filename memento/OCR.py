import cv2
from PIL import Image
from tesserocr import PyTessBaseAPI, RIL


class OCR:
    def __init__(self):
        pass

    def process_image(self, im):
        raise NotImplementedError

    def preprocess(self, im):
        im = cv2.resize(im, (0, 0), fx=self.rf, fy=self.rf)
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

        thr2 = cv2.bitwise_not(gray)
        thr2 = cv2.adaptiveThreshold(
            thr2, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

        thr = thr2
        cl = cv2.cvtColor(thr, cv2.COLOR_GRAY2BGR)
        return cl, thr

    def convert_texttron_bbox_format(self, bboxes, minAreaThreshold=100):
        new_bboxes = []
        for bbox in bboxes:
            x = bbox[0]
            y = bbox[1]
            w = bbox[2]
            h = bbox[3]
            area = w * h
            if area < minAreaThreshold:
                continue
            x1 = x
            x2 = x + w
            y1 = y
            y2 = y + h
            new_bboxes.append([x1, x2, y1, y2])
        return new_bboxes


class Tesseract(OCR):
    def __init__(self, langs="eng+fra", resize_factor=1, conf_threshold=50):
        super().__init__()
        self.langs = langs
        self.rf = resize_factor
        self.conf_threshold = conf_threshold
        self.api = PyTessBaseAPI(psm=11, oem=3)

    def process_image(self, im):
        im_shape = im.shape
        im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
        im = cv2.resize(im, (0, 0), fx=self.rf, fy=self.rf)
        im = Image.fromarray(im)
        self.api.SetImage(im)
        boxes = self.api.GetComponentImages(RIL.TEXTLINE, True)
        results = []
        _bboxes = []
        for i, (im, box, _, _) in enumerate(boxes):
            self.api.SetRectangle(box["x"], box["y"], box["w"], box["h"])

            ocrResult = self.api.GetUTF8Text()
            conf = self.api.MeanTextConf()

            if conf < self.conf_threshold:
                continue

            entry = {
                "x": box["x"] // self.rf,
                "y": box["y"] // self.rf,
                "w": box["w"] // self.rf,
                "h": box["h"] // self.rf,
                "text": ocrResult,
                "conf": conf,
            }

            _bboxes.append([entry["x"], entry["y"], entry["w"], entry["h"]])

            results.append(entry)

        return results
