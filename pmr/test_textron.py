import cv2
from TextTron.TextTron import TextTron
import time
import easyocr

# import pytesseract
# from pytesseract import Output
import numpy as np
from process import draw_results


def merge_near_bboxes(bboxes, close_dist=20):
    """
    Merge bounding boxes of words into paragraphs based on proximity.
    :param bboxes: list of bounding boxes of format [x, y, w, h]
    :param close_dist: maximum distance between two bounding boxes to be considered close
    :return: list of merged bounding boxes of format [x1, x2, y1, y2]
    """
    merged_bboxes = []
    for bbox in bboxes:
        # Check if bbox is close to any existing merged bbox
        merged = False
        for i, merged_bbox in enumerate(merged_bboxes):
            bbox_center = [bbox[0] + bbox[2] / 2, bbox[1] + bbox[3] / 2]
            merged_bbox_center = [
                merged_bbox[0] + (merged_bbox[1] - merged_bbox[0]) / 2,
                merged_bbox[2] + (merged_bbox[3] - merged_bbox[2]) / 2,
            ]
            dist = np.linalg.norm(np.array(bbox_center) - np.array(merged_bbox_center))

            if dist <= close_dist:
                # Merge bbox with existing merged bbox
                merged_bboxes[i][3] = bbox[3]
                merged = True
                break
        if not merged:
            # Add new merged bbox
            merged_bboxes.append(
                [bbox[0], bbox[0] + bbox[2], bbox[1], bbox[1] + bbox[3]]
            )
    return merged_bboxes


# TODO tune this threshold
def convert_bbox_format(bboxes, minAreaThreshold=100):
    new_bboxes = []
    for bbox in bboxes:
        x = bbox[0]
        y = bbox[1]
        w = bbox[2]
        h = bbox[3]
        area = w * h
        if area < minAreaThreshold:
            print("area too small")
            continue
        x1 = x
        x2 = x + w
        y1 = y
        y2 = y + h
        new_bboxes.append([x1, x2, y1, y2])
    return new_bboxes


easyocr_reader = easyocr.Reader(["fr", "en"], gpu=True)
# horizontal_list, free_list = easyocr_reader.detect(im)

total_time = time.time()

# TODO find out why cv2 resize bugs when resize_factor is 2
resize_factor = 2
orig_im = cv2.imread("test2.png")
im = cv2.resize(orig_im.copy(), (0, 0), fx=1 / resize_factor, fy=1 / resize_factor)
gry = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
if gry.mean() > 127:
    thr = cv2.adaptiveThreshold(
        gry, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 57, 1.0
    )

else:
    thr = cv2.adaptiveThreshold(
        gry, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 57, 1.0
    )

cl = cv2.cvtColor(thr, cv2.COLOR_GRAY2BGR)
start = time.time()
TT = TextTron(cl)
cv2.imwrite("plot.png", TT.plotImg)
print("Textron processing time :", time.time() - start)

merged_bboxes = merge_near_bboxes(TT.textBBox)

# for bbox in merged_bboxes:
#     x = bbox[0]
#     y = bbox[2]
#     w = bbox[1] - bbox[0]
#     h = bbox[3] - bbox[2]
#     im = cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 2)
# cv2.imwrite("merged.png", im)
# exit()


hl = [convert_bbox_format(TT.textBBox)]

# horizontal_list, free_list = easyocr_reader.detect(im)

start = time.time()
results = easyocr_reader.recognize(gry, horizontal_list=hl[0], free_list=[])
print("easyocr processing time :", time.time() - start)
res = []
for result in results:
    bb = np.array(result[0])
    text = result[1]
    conf = result[2]
    if conf < 0.1:
        continue
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

im_res = draw_results(res, orig_im)
cv2.imwrite("res.png", im_res)

print("Total processing time :", time.time() - total_time)
