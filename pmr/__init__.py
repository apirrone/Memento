
from pmr.background import Background
import pmr.background
import pmr.query_db


def bg():
    backgound = Background()
    backgound.run()


def query():
    pmr.query_db.query_db()
