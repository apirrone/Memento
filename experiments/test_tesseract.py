import cv2
import numpy as np
import mss
import time
import pytesseract
from pytesseract import Output
import pickle

# sct = mss.mss()
# time.sleep(1)
# im = np.array(sct.grab(sct.monitors[1]))
# im = im[:, :, :-1]
# im = cv2.resize(im, utils.RESOLUTION)
# cv2.imwrite("test.png", im)
# exit()


def preprocess_image(im, rf=1):
    im = cv2.resize(im, (0, 0), fx=rf, fy=rf)
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    thr2 = cv2.bitwise_not(gray)
    thr2 = cv2.adaptiveThreshold(
        thr2, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    thr = thr2
    cl = cv2.cvtColor(thr, cv2.COLOR_GRAY2BGR)
    return cl, thr


def process_image(im, preprocess=True, rf=1):
    thr = im
    if preprocess:
        cl, thr = preprocess_image(im, rf=rf)

    custom_oem_psm_config = r"--oem 3 --psm 3"  # 11
    results = pytesseract.image_to_data(
        thr,
        output_type=Output.DICT,
        lang="eng+fra",
        config=custom_oem_psm_config,
    )
    pickle.dump(results, open("results.pkl", "wb"))

    # results = pickle.load(open("results.pkl", "rb"))
    blocks = {}
    words = []
    for i, level in enumerate(results["level"]):
        conf = results["conf"][i]
        x = results["left"][i]
        y = results["top"][i]
        w = results["width"][i]
        h = results["height"][i]
        text = results["text"][i]
        word_num = results["word_num"][i]
        line_num = results["line_num"][i]
        block_num = results["block_num"][i]
        par_num = results["par_num"][i]
        # print(level, conf, x, y, w, h, text, word_num, line_num, block_num, par_num)
        if level == 2:  # block
            if block_num not in blocks:
                blocks[block_num] = {}
                blocks[block_num]["x"] = x // rf
                blocks[block_num]["y"] = y // rf
                blocks[block_num]["w"] = w // rf
                blocks[block_num]["h"] = h // rf
                blocks[block_num]["text"] = []

        if level == 5:  # word
            if conf > 80:
                blocks[block_num]["text"].append(text)
                words.append(
                    {
                        "x": x // rf,
                        "y": y // rf,
                        "w": w // rf,
                        "h": h // rf,
                        "text": text,
                    }
                )

    return blocks, words


def draw_words(im, words):
    for word in words:
        x = word["x"]
        y = word["y"]
        w = word["w"]
        h = word["h"]
        text = word["text"]
        im = cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 2)
    return im


def draw_blocks(im, blocks):
    for block_num in blocks:
        block = blocks[block_num]
        x = block["x"]
        y = block["y"]
        w = block["w"]
        h = block["h"]
        text = " ".join(block["text"])
        im = cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 2)
        # im = cv2.putText(
        #     im,
        #     text,
        #     (x, y),
        #     cv2.FONT_HERSHEY_SIMPLEX,
        #     1,
        #     (0, 255, 0),
        #     1,
        #     cv2.LINE_AA,
        # )
    return im


for i in range(4):
    im = cv2.imread(str(i) + ".png")

    start = time.time()
    blocks, words = process_image(im, preprocess=True, rf=2)
    print("Processing time :", time.time() - start)
    # im = draw_blocks(im, blocks)
    im = draw_words(im, words)
    cv2.imwrite("out" + str(i) + ".png", im)
    # print("nb paragraphs", len(paragraphs))

# res_im = utils.draw_results(paragraphs, im)
# cv2.imwrite("out_preprocess.png", res_im)
# cv2.imwrite("out.png", res_im)
