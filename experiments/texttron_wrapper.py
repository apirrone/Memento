from TextTron.TextTron import TextTron


class BBox:
    # x1, x2, y1, y2
    def __init__(self, bbox):
        self.bbox = bbox
        self.area = (self.bbox[1] - self.bbox[0]) * (self.bbox[3] - self.bbox[2])

    def contains(self, bbox):
        return (
            bbox[0] >= self.bbox[0]
            and bbox[1] <= self.bbox[1]
            and bbox[2] >= self.bbox[2]
            and bbox[3] <= self.bbox[3]
        )

    def get_area(self):
        return self.area

    def get_bbox(self):
        return self.bbox


class BBoxes:
    def __init__(self, bboxes):
        self.bboxes = []

        for bbox in bboxes:
            bbox = BBox(bbox)
            self.bboxes.append((bbox.area, bbox))

        # sort by area
        self.bboxes.sort(key=lambda x: x[0], reverse=True)

    def merge(self):
        to_remove = []
        for i in range(len(self.bboxes)):
            for j in range(len(self.bboxes)):
                if i == j or i in to_remove or j in to_remove:
                    continue

                bb1 = self.bboxes[i][1]
                bb2 = self.bboxes[j][1]

                if bb1.contains(bb2.bbox):  # remove bb2
                    to_remove.append(j)

        to_remove = sorted(to_remove, reverse=True)
        for idx in to_remove:
            self.bboxes.pop(idx)

    def get(self):
        ret = []
        for bbox in self.bboxes:
            ret.append(bbox[1].get_bbox())

        return ret


class TexttronWrapper:
    def __init__(self, im, xThreshold=5, yThreshold=2):
        self.im = im
        self.tt = TextTron(im, xThreshold=xThreshold, yThreshold=yThreshold)
        self.bboxes = self.convert(self.tt.textBBox)
        self.bboxes = BBoxes(self.bboxes)
        self.bboxes.merge()
        self.bboxes = self.bboxes.get()

    def convert(self, bboxes, minAreaThreshold=100):
        new_bboxes = []
        for bbox in bboxes:
            x = bbox[0]
            y = bbox[1]
            w = bbox[2]
            h = bbox[3]
            area = w * h
            if area < minAreaThreshold:
                continue
            x1 = x
            x2 = x + w
            y1 = y
            y2 = y + h
            new_bboxes.append([x1, x2, y1, y2])
        return new_bboxes
