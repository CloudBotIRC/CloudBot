from datetime import datetime

from sqlalchemy import Table, Column, String, Boolean, Integer, DateTime
from sqlalchemy.sql import select

from cloudbot import hook
from cloudbot.util import botvars

table = Table(
    'notes',
    botvars.metadata,
    Column('note_id', Integer, primary_key=True, unique=True, autoincrement=True),
    Column('connection', String),
    Column('user', String),
    Column('text', String),
    Column('priority', Integer),
    Column('deleted', Boolean),
    Column('added', DateTime),
)


def read_all_notes(db, server, user, show_deleted=False):
    query = select([table.c.note_id, table.c.text, table.c.added]) \
        .where(table.c.connection == server) \
        .where(table.c.user == user.lower()) \
        .where(table.c.deleted == show_deleted) \
        .order_by(table.c.added)
    return db.execute(query).fetchall()


def read_note(db, server, user, note_id):
    query = table.select() \
        .where(table.c.connection == server) \
        .where(table.c.user == user.lower()) \
        .where(table.c.note_id == note_id)
    return db.execute(query).fetchall()


def add_note(db, server, user, text):
    query = table.insert().values(
        connection=server,
        user=user.lower(),
        text=text,
        deleted=False,
        added=datetime.today()
    )
    db.execute(query)
    db.commit()


@hook.command("note", "notes")
def note(text, conn, nick, db, notice):
    """<add|list|get> args - manipulates your list of notes"""
    parts = text.split()
    cmd = parts[0].lower()

    args = parts[1:]

    # code to allow users to access each others factoids and a copy of help
    # ".note (add|del|list|search) [@user] args -- Manipulates your list of todos."
    # if len(args) and args[0].startswith("@"):
    # nick = args[0][1:]
    #    args = args[1:]

    if cmd == 'add':
        if not len(args):
            return "no text"

        text = " ".join(args)

        add_note(db, conn.name, nick, text)

        notice("Note added!")
        return
    elif cmd == 'get':
        notes = read_note(db, conn.name, nick, text)

        if not notes:
            notice("{} has no entries.".format(nick))

        for n in notes:
            note_id, note, added = n
            notice("#{}: {} - {}".format(note_id, note, added))
    elif cmd == 'list':
        notes = read_all_notes(db, conn.name, nick)

        if not notes:
            notice("{} has no entries.".format(nick))

        for n in notes:
            note_id, note, added = n
            notice("#{}: {} - {}".format(note_id, note, added))

    else:
        notice("Unknown command: {}".format(cmd))
