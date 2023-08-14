import layoutparser as lp
import cv2

im = cv2.imread("test.png")
im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)

model = lp.Detectron2LayoutModel(
    "lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config",
    extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.8],
    label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"},
)
