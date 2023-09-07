from memento.background import Background
from memento.timeline.timeline import Timeline


def bg():
    backgound = Background()
    backgound.run()


def tl():
    t = Timeline()
    t.run()
