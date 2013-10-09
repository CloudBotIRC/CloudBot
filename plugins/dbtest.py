from util import hook

from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker

def create_tables(metadata):
    users_table = Table('users', metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String),
        Column('fullname', String),
        Column('password', String)
    )
    users_table.create()


@hook.command
def dbtest(inp, db=None):
    metadata = MetaData(db)
    create_tables(metadata)
    print metadata