from pmr.background import Background
from pmr.query_db import Query
from pmr.timeline.timeline import Timeline


def bg():
    backgound = Background()
    backgound.run()


def query():
    q = Query()
    # i = input("query : ")
    i = "luxonis"
    print(q.query_db(i))


def tl():
    t = Timeline()
    t.run()
