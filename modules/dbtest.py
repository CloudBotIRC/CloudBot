from util import hook
from sqlalchemy import Table, Column, String, MetaData

metadata = MetaData()
users = Table('user_table', metadata,
              Column('name', String),
              Column('phone', String)
)


@hook.command
def adduser(text, db):
    # create tables
    metadata.bind = db
    metadata.create_all()

    # create DB connection
    connection = db.connect()

    data = text.split()
    values = {
        "name": data[0],
        "phone": data[1]
    }

    query = users.insert(values=values)
    connection.execute(query)


@hook.command(autohelp=False)
def select(db, message):
    # create tables
    metadata.bind = db
    metadata.create_all()

    # create DB connection
    connection = db.connect()

    results = connection.execute(users.select())
    for row in results:
        message("name: {}, phone: {}".format(row.name, row.phone))



