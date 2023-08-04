import cv2
import numpy as np
from TextTron.TextTron import TextTron
import easyocr
import pytesseract
from pytesseract import Output
import pmr.utils as utils


class OCR:
    def __init__(self):
        pass

    def process_image(self, im):
        raise NotImplementedError

    def preprocess(self, im):
        im = cv2.resize(im, (0, 0), fx=self.rf, fy=self.rf)
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        if gray.mean() > 127:
            thr = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 57, 1.0
            )

        else:
            thr = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 57, 1.0
            )
        cl = cv2.cvtColor(thr, cv2.COLOR_GRAY2BGR)
        return cl, thr


class EasyOCR(OCR):
    def __init__(
        self, langs=["fr", "en"], gpu=True, resize_factor=2, conf_threshold=0.1
    ):
        super().__init__()
        self.rf = resize_factor
        self.conf_threshold = conf_threshold

        self.reader = easyocr.Reader(langs, gpu=gpu)

    def process_image(self, im):
        cl, thr = self.preprocess(im)
        # get text bounding boxes
        TT = TextTron(cl)
        bboxes = self.convert_bbox_format(TT.textBBox)

        # run easyocr on the image using the bounding boxes
        results = self.reader.recognize(thr, horizontal_list=bboxes, free_list=[])

        # convert results to our format
        res = []
        for result in results:
            bb = np.array(result[0])
            text = result[1]
            conf = result[2]
            if conf < self.conf_threshold:
                continue
            x = bb[0][0] // self.rf
            y = bb[0][1] // self.rf
            w = (bb[2][0] - bb[0][0]) // self.rf
            h = (bb[2][1] - bb[0][1]) // self.rf
            entry = {
                "x": int(x),
                "y": int(y),
                "w": int(w),
                "h": int(h),
                "text": text,
                "conf": conf,
            }
            res.append(entry)

        return res

    def convert_bbox_format(self, bboxes, minAreaThreshold=100):
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
    def __init__(self, langs="eng+fra", resize_factor=2, conf_threshold=10):
        super().__init__()
        self.langs = langs
        self.rf = resize_factor
        self.conf_threshold = conf_threshold

    def process_image(self, im):
        cl, thr = self.preprocess(im)
        custom_oem_psm_config = r"--oem 3 --psm 11"
        results = pytesseract.image_to_data(
            thr,
            output_type=Output.DICT,
            lang=self.langs,
            config=custom_oem_psm_config,
        )

        # TODO check if I can do better by using the data returned by tesseract (page, block, paragraph hierarchy)
        paragraphs = {}
        for i in range(len(results["text"])):
            conf = int(results["conf"][i])
            if conf < self.conf_threshold:
                continue
            x = results["left"][i]
            y = results["top"][i]

            w = results["width"][i]
            h = results["height"][i]

            text = results["text"][i]
            entry = {
                "x": x // self.rf,
                "y": y // self.rf,
                "w": w // self.rf,
                "h": h // self.rf,
                "text": text,
                "conf": conf,
            }
            if results["block_num"][i] not in paragraphs:
                paragraphs[results["block_num"][i]] = entry
            else:
                px = paragraphs[results["block_num"][i]]["x"]
                py = paragraphs[results["block_num"][i]]["y"]
                px2 = px + paragraphs[results["block_num"][i]]["w"]
                py2 = py + paragraphs[results["block_num"][i]]["h"]

                ex = entry["x"]
                ey = entry["y"]
                ew = entry["w"]
                eh = entry["h"]
                ex2 = ex + ew
                ey2 = ey + eh

                paragraphs[results["block_num"][i]]["text"] += " " + entry["text"]
                paragraphs[results["block_num"][i]]["x"] = min(px, ex)
                paragraphs[results["block_num"][i]]["y"] = min(py, ey)
                paragraphs[results["block_num"][i]]["w"] = (
                    max(px2, ex2) - paragraphs[results["block_num"][i]]["x"]
                )
                paragraphs[results["block_num"][i]]["h"] = (
                    max(py2, ey2) - paragraphs[results["block_num"][i]]["y"]
                )
        # TODO tune this tol, make something better ? no overlapping bbs ?
        # With tol very high, it takes pretty much the whole screen.
        # Easy to test with 1 document = 1 screenshot
        return utils.make_paragraphs(list(paragraphs.values()), tol=5000)

    # TODO replace tolerances in pixels by tolerances in percentage of the image size
    def merge_boxes(self, res, x_tol=50, y_tol=20):
        lines_indices = {}
        for i, entry in enumerate(res):
            y = entry["y"]

            line = utils.line_exists(y, lines_indices, y_tol=y_tol)
            if line is None:
                lines_indices[y] = []
                lines_indices[y].append(i)
            else:
                lines_indices[line].append(i)

        new_res = []

        for line in lines_indices.values():
            sentences = []
            first_word = True
            for word in line:
                x = res[word]["x"]
                y = res[word]["y"]
                w = res[word]["w"]
                h = res[word]["h"]
                text = res[word]["text"]
                if not first_word and utils.same_sentence(
                    sentences[-1], x, x_tol=x_tol
                ):
                    sentences[-1]["w"] = x + w - sentences[-1]["x"]
                    sentences[-1]["text"] += " " + text
                    if sentences[-1]["h"] < h:
                        sentences[-1]["h"] = h
                else:
                    entry = {
                        "x": x,
                        "y": y,
                        "w": w,
                        "h": h,
                        "text": text,
                    }
                    sentences.append(entry)
                    first_word = False
            for sentence in sentences:
                new_res.append(sentence)
        return new_res
