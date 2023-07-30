from pmr.background import Background
import pmr.background
import pmr.query_db


def bg():
    backgound = Background()
    backgound.run()


def query():
    q = pmr.query_db.Query()
    i = input("query : ")
    q.query_db(i)
