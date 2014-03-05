from util import hook

from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker

@hook.command
def dbtest(inp, db=None):
    print(db)