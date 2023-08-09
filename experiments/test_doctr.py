import cv2
import numpy as np
from doctr.models import ocr_predictor
from doctr.io import DocumentFile
import time

# im = cv2.imread("test.png")
model = ocr_predictor(det_arch='db_resnet50', reco_arch='crnn_vgg16_bn', pretrained=True, assume_straight_pages=True)

doc = DocumentFile.from_images("test.png")

start = time.time()
result = model(doc)
print("processing time: ", time.time() - start)
# import matplotlib.pyplot as plt

# synthetic_pages = result.synthesize()
# plt.imshow(synthetic_pages[0]); plt.axis('off'); plt.show()
result.show(doc)
