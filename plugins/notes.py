from datetime import datetime

from sqlalchemy import Table, Column, String, Boolean, Integer, DateTime
import sqlalchemy
from sqlalchemy.sql import select

from cloudbot import hook
from cloudbot.util import botvars

table = Table(
    'notes',
    botvars.metadata,
    Column('note_id', Integer, primary_key=True, autoincrement=True),
    Column('connection', String, primary_key=True),
    Column('user', String, primary_key=True),
    Column('text', String),
    Column('priority', Integer),
    Column('deleted', Boolean),
    Column('added', DateTime),
)


def read_all_notes(db, server, user, show_deleted=False):
    if show_deleted:
        query = select([table.c.note_id, table.c.text, table.c.added]) \
            .where(table.c.connection == server) \
            .where(table.c.user == user.lower()) \
            .order_by(table.c.added)
    else:
        query = select([table.c.note_id, table.c.text, table.c.added]) \
            .where(table.c.connection == server) \
            .where(table.c.user == user.lower()) \
            .where(table.c.deleted == 0) \
            .order_by(table.c.added)
    return db.execute(query).fetchall()


def delete_all_notes(db, server, user):
    query = table.update() \
        .where(table.c.connection == server) \
        .where(table.c.user == user.lower()) \
        .values(deleted=1)
    db.execute(query)
    db.commit()


def read_note(db, server, user, note_id):
    query = select() \
        .where(table.c.connection == server) \
        .where(table.c.user == user.lower()) \
        .where(table.c.note_id == note_id)
    return db.execute(query).fetchone()[0]


def delete_note(db, server, user, note_id):
    query = table.update() \
        .where(table.c.connection == server) \
        .where(table.c.user == user.lower()) \
        .where(table.c.note_id == note_id) \
        .values(deleted=1)
    db.execute(query)
    db.commit()


def add_note(db, server, user, text):
    id_query = select([sqlalchemy.sql.expression.func.max(table.c.note_id).label("maxid")]) \
        .where(table.c.user == user.lower())
    max_id = db.execute(id_query).scalar()

    if max_id is None:
        note_id = 1
    else:
        note_id = max_id + 1

    query = table.insert().values(
        note_id = note_id,
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
            return

        notice("All notes for {}:".format(nick))

        for n in notes:
            note_id, note, added = n
            notice("#{}: {} - {}".format(note_id, note, added))

    else:
        notice("Unknown command: {}".format(cmd))
