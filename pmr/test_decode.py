from utils import Reader
import cv2

reader = Reader("test.mp4")

cv2.imshow("aze", reader.get_frame(20))

cv2.waitKey(0)
