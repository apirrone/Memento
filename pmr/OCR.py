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
        im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
        im = cv2.resize(im, (0, 0), fx=self.rf, fy=self.rf)
        im = Image.fromarray(im)
        self.api.SetImage(im)
        boxes = self.api.GetComponentImages(RIL.TEXTLINE, True)
        results = []

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

            results.append(entry)

        return results


# class EasyOCR(OCR):
#     def __init__(
#         self, langs=["fr", "en"], gpu=True, resize_factor=2, conf_threshold=0.1
#     ):
#         super().__init__()
#         self.rf = resize_factor
#         self.conf_threshold = conf_threshold

#         self.reader = easyocr.Reader(langs, gpu=gpu)

#     def process_image(self, im):
#         cl, thr = self.preprocess(im)
#         # get text bounding boxes
#         TT = TextTron(cl)
#         bboxes = self.convert_bbox_format(TT.textBBox)

#         # run easyocr on the image using the bounding boxes
#         results = self.reader.recognize(thr, horizontal_list=bboxes, free_list=[])

#         # convert results to our format
#         res = []
#         for result in results:
#             bb = np.array(result[0])
#             text = result[1]
#             conf = result[2]
#             if conf < self.conf_threshold:
#                 continue
#             x = bb[0][0] // self.rf
#             y = bb[0][1] // self.rf
#             w = (bb[2][0] - bb[0][0]) // self.rf
#             h = (bb[2][1] - bb[0][1]) // self.rf
#             entry = {
#                 "x": int(x),
#                 "y": int(y),
#                 "w": int(w),
#                 "h": int(h),
#                 "text": text,
#                 "conf": conf,
#             }
#             res.append(entry)

#         return res

#     def convert_bbox_format(self, bboxes, minAreaThreshold=100):
#         new_bboxes = []
#         for bbox in bboxes:
#             x = bbox[0]
#             y = bbox[1]
#             w = bbox[2]
#             h = bbox[3]
#             area = w * h
#             if area < minAreaThreshold:
#                 continue
#             x1 = x
#             x2 = x + w
#             y1 = y
#             y2 = y + h
#             new_bboxes.append([x1, x2, y1, y2])
#         return new_bboxes
