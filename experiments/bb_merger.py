from memento.OCR import Tesseract
import memento.utils as utils
import cv2
import pickle
import numpy as np

im = cv2.imread("test0.png")

ocr = Tesseract(resize_factor=0.5)
# ocr = EasyOCR(resize_factor=1)
res = ocr.process_image(im)
# pickle.dump(res, open("res.pkl", "wb"))
# res = pickle.load(open("res.pkl", "rb"))

imraw = utils.draw_results(res, im.copy())
par = utils.make_paragraphs(res)
im_par = utils.draw_results(par, im)
cv2.imwrite("test0_words.png", imraw)
cv2.imwrite("test0_par.png", im_par)
