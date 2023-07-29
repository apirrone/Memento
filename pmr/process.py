import cv2
import pytesseract
from pytesseract import Output
import pmr.utils as utils


# TODO : split the box by x_tol too
def merge_boxes(res):
    lines_indices = {}
    for i, entry in enumerate(res):
        y = entry["y"]

        line = utils.line_exists(y, lines_indices, y_tol=20)
        if line is None:
            lines_indices[y] = []
            lines_indices[y].append(i)
        else:
            lines_indices[line].append(i)

    lines = {}
    new_res = []
    for line_index, line in lines_indices.items():
        min_x = 1000000000
        max_x = 0
        min_y = 1000000000
        max_h = 0
        lines[line_index] = ""
        for word in line:
            x = res[word]["x"]
            w = res[word]["w"]
            if x < min_x:
                min_x = x
            if x + w > max_x:
                max_x = x + w
            if res[word]["y"] < min_y:
                min_y = res[word]["y"]
            if res[word]["h"] > max_h:
                max_h = res[word]["h"]
            lines[line_index] += res[word]["text"] + " "

        entry = {
            "x": min_x,
            "y": min_y,
            "w": max_x - min_x,
            "h": max_h,
            "text": lines[line_index],
        }
        new_res.append(entry)

    return new_res


def process_image(image, conf_threshold=80):
    results = pytesseract.image_to_data(
        image,
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