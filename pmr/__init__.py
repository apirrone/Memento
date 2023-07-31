from pmr.background import Background
import pmr.background
import pmr.query_db
import pmr.timeline


def bg():
    backgound = Background()
    backgound.run()


def query():
    q = pmr.query_db.Query()
    # i = input("query : ")
    i = "luxonis"
    print(q.query_db(i))


def tl():
    t = pmr.timeline.Timeline()
    t.run()
