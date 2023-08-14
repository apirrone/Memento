# import tesserocr
import cv2
from PIL import Image
import time
from tesserocr import PyTessBaseAPI, PSM, OEM, RIL

imgs = ["0.png", "1.png", "2.png", "3.png", "4.png"]
# imgs = ["0.png"]

box = (280, 290, 1700, 560)
# with PyTessBaseAPI(psm=PSM.OSD_ONLY, oem=OEM.LSTM_ONLY) as api:
with PyTessBaseAPI() as api:
    for img in imgs:
        start = time.time()
        im = cv2.cvtColor(cv2.imread(img), cv2.COLOR_BGR2RGB)
        im = Image.fromarray(im)
        api.SetImage(im)
        api.SetRectangle(box[0], box[1], box[2], box[3])
        ocrResult = api.GetUTF8Text()
        print(time.time() - start)
        # print(ocrResult)