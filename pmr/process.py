import cv2
import pytesseract
from pytesseract import Output
import pmr.utils as utils

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


def process_image(image, conf_threshold=10):
    results = pytesseract.image_to_data(
        image,  # Maybe resize the image here for better detection ?
        output_type=Output.DICT,
    )
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

    return merge_boxes(res)  # make lines


def draw_results(res, image):
    for entry in res:
        x = entry["x"]
        y = entry["y"]
        w = entry["w"]
        h = entry["h"]
        # text = entry["text"]
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        # cv2.putText(
        #     image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 200), 2
        # )

    return image
