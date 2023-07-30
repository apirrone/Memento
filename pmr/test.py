import cv2  
from pmr.process import process_image, draw_results

im = cv2.imread("../screenshots/0.png")

results = process_image(im)
im = draw_results(results, im)
cv2.imshow("im", im)
cv2.waitKey(0)