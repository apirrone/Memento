import cv2
import pytesseract
from pytesseract import Output
import pmr.utils as utils
import numpy as np


# TODO replace tolerances in pixels by tolerances in percentage of the image size
def merge_boxes(res, x_tol=50, y_tol=20):
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
            if not first_word and utils.same_sentence(sentences[-1], x, x_tol=x_tol):
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


def process_image_easyocr(image, reader, conf_threshold=0.1, batch_size=4):
    resize_factor = 2
    image = cv2.resize(image, (0, 0), fx=1 / resize_factor, fy=1 / resize_factor)
    # image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    results = reader.readtext(image, batch_size=batch_size)
    res = []
    for result in results:
        bb = np.array(result[0])
        text = result[1]
        conf = result[2]
        if conf < conf_threshold:
            continue
        print(conf)
        x = bb[0][0] * resize_factor
        y = bb[0][1] * resize_factor
        w = (bb[2][0] - bb[0][0]) * resize_factor
        h = (bb[2][1] - bb[0][1]) * resize_factor
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


def preprocess_image_ocr(image):
    #screenshot are 72x72dpi?
    img = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    gry = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if gry.mean() > 127:
        thr = cv2.adaptiveThreshold(gry, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                    cv2.THRESH_BINARY, 57, 1.0)

    else:
        thr = cv2.adaptiveThreshold(gry, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                    cv2.THRESH_BINARY_INV, 57, 1.0)


    # cv2.imwrite("pre.png", thr)
    return thr

def process_image_tesseract(image, conf_threshold=10):
    custom_oem_psm_config = r'--oem 3 --psm 11'
    results = pytesseract.image_to_data(
        preprocess_image_ocr(image),  # Maybe resize the image here for better detection ?
        output_type=Output.DICT,
        lang="eng+fra",
        config=custom_oem_psm_config

    )
    # results = pytesseract.image_to_data(
    #     image,  # Maybe resize the image here for better detection ?
    #     output_type=Output.DICT,
    # )

    res = []
    for i in range(len(results["text"])):
        conf = int(results["conf"][i])
        if conf < conf_threshold:
            continue
        x = results["left"][i]
        y = results["top"][i]

        w = results["width"][i]
        h = results["height"][i]

        text = results["text"][i]
        entry = {
            "x": x,
            "y": y,
            "w": w,
            "h": h,
            "text": text,
            "conf": conf,
        }
        res.append(entry)

        #    return merge_boxes(res)  # make lines
    return res

def process_image(image, ocr="tesseract", reader=None):
    if ocr == "tesseract":
        return process_image_tesseract(image)
    elif ocr == "easyocr":
        return process_image_easyocr(image, reader=reader)
    else:
        print("Unknown ocr engine")


def draw_results(res, image):
    for entry in res:
        x = entry["x"]//2 #because I make a resize factor 2
        y = entry["y"]//2
        w = entry["w"]//2
        h = entry["h"]//2
        text = entry["text"]

        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(
            image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 200), 2
        )

    return image
