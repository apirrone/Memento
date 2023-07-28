import cv2
from glob import glob
import pytesseract
from pytesseract import Output


def process_image(image):
    results = pytesseract.image_to_data(
        image,
        output_type=Output.DICT,
    )

    return results


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
