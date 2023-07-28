import cv2
from glob import glob
import pytesseract
from pytesseract import Output

imagesPaths = glob("screenshots/*.png")
images = []
for imagePath in imagesPaths:
    images.append(cv2.imread(imagePath))

for k, image in enumerate(images):
    image = cv2.resize(image, (0, 0), fx=3, fy=3)
    results = pytesseract.image_to_data(image, output_type=Output.DICT)

    for i in range(0, len(results["text"])):
        x = results["left"][i]
        y = results["top"][i]

        w = results["width"][i]
        h = results["height"][i]

        text = results["text"][i]
        conf = int(results["conf"][i])

        if conf > 70:
            text = "".join([c if ord(c) < 128 else "" for c in text]).strip()
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(
                image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 200), 2
            )
    cv2.imwrite("processed/" + str(k) + ".png", image)
    print("processed " + str(k))
