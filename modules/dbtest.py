from util import hook
from sqlalchemy import Table, Column, String, MetaData

metadata = MetaData()
users = Table('user_table', metadata,
              Column('name', String),
              Column('phone', String)
)


def init_db(db):
    metadata.bind = db
    metadata.create_all()


@hook.command
def adduser(text, db):
    init_db(db)

    # create DB connection
    connection = db.connect()

    data = text.split()
    values = {
        "name": data[0],
        "phone": data[1]
    }

    query = users.insert(values=values)
    # OR users.insert().values(**values) - http://docs.sqlalchemy.org/en/rel_0_9/core/tutorial.html

    connection.execute(query)


@hook.command(autohelp=False)
def select(db, message):
    init_db(db)

    # create DB connection
    connection = db.connect()

    results = connection.execute(users.select())
    for row in results:
        message("name: {}, phone: {}".format(row.name, row.phone))
