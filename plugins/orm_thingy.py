from sqlalchemy import Column, Integer, String, Sequence

from cloudbot import hook
from cloudbot.util.database import base


class User(base):
    __tablename__ = 'users_'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    name = Column(String(50))
    data = Column(String(100))

base.metadata.create_all()

print(User)
print(User.__table__)

@hook.command
def test(text, db):
    name = text.split(" ", 1)[0]
    data = text.split(" ", 1)[1]

    ed_user = User(name=name, data=data)
    db.add(ed_user)
    db.commit()
    return "id: {}, name: {}, data: {}".format(ed_user.id, ed_user.name, ed_user.data)




