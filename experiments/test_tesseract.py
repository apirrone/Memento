import pytesseract
from pytesseract import Output
from pmr import utils

# import pmr.utils as utils
import cv2
import pickle
import numpy as np
from pmr.OCR import Tesseract

ts = Tesseract(resize_factor=1)  # just for preprocessing functino
im_name = "test3"
im = cv2.imread(im_name+".png")
# im = cv2.resize(im, (0, 0), fx=3, fy=3)
custom_oem_psm_config = r"--oem 3 --psm 11"
results = pytesseract.image_to_data(
    ts.preprocess(im)[1],
    output_type=Output.DICT,
    lang="eng+fra",
    config=custom_oem_psm_config,
)

paragraphs = {}
for i in range(len(results["text"])):
    conf = int(results["conf"][i])
    if conf < 10:
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
    if results["block_num"][i] not in paragraphs:
        paragraphs[results["block_num"][i]] = entry
    else:
        px = paragraphs[results["block_num"][i]]["x"]
        py = paragraphs[results["block_num"][i]]["y"]
        px2 = px + paragraphs[results["block_num"][i]]["w"]
        py2 = py + paragraphs[results["block_num"][i]]["h"]
        pw = paragraphs[results["block_num"][i]]["w"]
        ph = paragraphs[results["block_num"][i]]["h"]

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


res_im = utils.draw_results(paragraphs.values(), im)
cv2.imwrite(im_name+"_par.png", res_im)
