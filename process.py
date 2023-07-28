import cv2
from glob import glob
import pytesseract
from pytesseract import Output


def process_image(image, conf_threshold=10):
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

    return res


def draw_results(res, image):
    for entry in res:
        x = entry["x"]
        y = entry["y"]
        w = entry["w"]
        h = entry["h"]
        text = entry["text"]
        conf = entry["conf"]
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(
            image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 200), 2
        )

    return image


# imagesPaths = glob("screenshots/*.png")
# images = []
# for imagePath in imagesPaths:
#     images.append(cv2.imread(imagePath))

# image_scale_factor = 1
# for k, image in enumerate(images):
#     results = pytesseract.image_to_data(
#         cv2.resize(image, (0, 0), fx=image_scale_factor, fy=image_scale_factor),
#         output_type=Output.DICT,
#     )

#     for i in range(0, len(results["text"])):
#         x = results["left"][i] // image_scale_factor
#         y = results["top"][i] // image_scale_factor

#         w = results["width"][i] // image_scale_factor
#         h = results["height"][i] // image_scale_factor

#         text = results["text"][i]
#         conf = int(results["conf"][i])

#         if conf > 10:
#             text = "".join([c if ord(c) < 128 else "" for c in text]).strip()
#             cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
#             cv2.putText(
#                 image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 200), 2
#             )

#     cv2.imwrite("processed/a" + str(k) + ".png", image)
#     print("processed " + str(k))
