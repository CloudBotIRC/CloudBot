import random
import re
import operator

from time import time
from collections import defaultdict
from sqlalchemy import Table, Column, String, Integer, PrimaryKeyConstraint, desc
from sqlalchemy.sql import select
from cloudbot import hook
from cloudbot.event import EventType
from cloudbot.util import botvars

duck_tail = "・゜゜・。。・゜゜"
duck = "\_o< "
duck_noise = ["QUACK!", "FLAP FLAP FLAP!", "quack quack quack!"]

table = Table(
    'duck_hunt',
    botvars.metadata,
    Column('network', String),
    Column('name', String),
    Column('shot', Integer),
    Column('befriend', Integer),
    Column('chan', String),
    PrimaryKeyConstraint('name', 'chan','network')
    )

opt_out = ['#anxiety', '#physics', '#UkrainianConflict']

"""
game_status structure 
{ 
    'network':{
        '#chan1':{
            'duck_status':0|1|2, 
            'next_duck_time':'integer', 
            'game_started':0|1,
            'no_duck_kick': 0|1,
            'duck_time': 'float', 
            'shoot_time': 'float'
        }
    }
}
"""

scripters = defaultdict(int)
game_status = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))


@hook.command("starthunt", autohelp=False)
def start_hunt(bot, chan, message, conn):
    """This command starts a duckhunt in your channel, to stop the hunt use .stophunt"""
    global game_status
    if chan in opt_out:
        return
    check = game_status[conn.name][chan]['game_on']
    if check:
        return "there is already a game running in {}.".format(chan)
    else:
        game_status[conn.name][chan]['game_on'] = 1
    set_ducktime(chan, conn)
    message("Ducks have been spotted nearby. See how many you can shoot or save. use .bang to shoot or .befriend to save them.", chan)

def set_ducktime(chan, conn):
    global game_status
    game_status[conn.name][chan]['next_duck_time'] = random.randint(int(time()) + 480, int(time()) + 3600)
    game_status[conn.name][chan]['duck_status'] = 0
    return

@hook.command("stophunt", autohelp=False)
def stop_hunt(chan, conn):
    """This command stops the duck hunt in your channel. Scores will be preserved"""
    global game_status
    if chan in opt_out:
        return
    if game_status[conn.name][chan]['game_on']:
        game_status[conn.name][chan]['game_on'] = 0
        return "the game has been stopped."
    else:
        return "There is no game running in {}.".format(chan)

@hook.command("duckkick")
def no_duck_kick(text, chan, conn, notice):
    """If the bot has OP or half-op in the channel you can specify .duckkick enable|disable so that people are kicked for shooting or befriending a non-existent goose. Default is off."""
    global game_status
    if chan in opt_out:
        return
    if text.lower() == 'enable':
        game_status[conn.name][chan]['no_duck_kick'] = 1
        return "users will now be kicked for shooting or befriending non-existent ducks. The bot needs to have appropriate flags to be able to kick users for this to work."
    elif text.lower() == 'disable':
        game_status[conn.name][chan]['no_duck_kick'] = 0
        return "kicking for non-existent ducks has been disabled."
    else:
        notice(no_duck_kick.__doc__)
        return

def generate_duck():
    """Try and randomize the duck message so people can't highlight on it/script against it."""
    rt = random.randint(1, len(duck_tail) -1)
    dtail = duck_tail[:rt] + u' \u200b ' + duck_tail[rt:]
    rb = random.randint(1, len(duck) - 1)
    dbody = duck[:rb] + u'\u200b' + duck[rb:]
    dnoise = random.choice(duck_noise)
    rn = random.randint(1, len(dnoise) - 1)
    dnoise = dnoise[:rn] + u'\u200b' + dnoise[rn:]
    return (dtail, dbody, dnoise)


@hook.periodic(11, initial_interval=11)
def deploy_duck(message, bot):
    global game_status
    for network in game_status:
        if network not in bot.connections:
            continue
        conn = bot.connections[network]
        if not conn.ready:
            continue
        for chan in game_status[network]:
            active = game_status[network][chan]['game_on']
            duck_status = game_status[network][chan]['duck_status']
            next_duck = game_status[network][chan]['next_duck_time']
            if active == 1 and duck_status == 0 and next_duck <= time():
                #deploy a duck to channel
                game_status[network][chan]['duck_status'] = 1
                game_status[network][chan]['duck_time'] = time()
                dtail, dbody, dnoise = generate_duck()
                conn.message(chan, "{}{}{}".format(dtail, dbody, dnoise))
            continue
        continue


def hit_or_miss(deploy, shoot):
    """This function calculates if the befriend or bang will be successful."""
    if shoot - deploy < .7:
        return .05
    elif .7 <= shoot - deploy <=3:
        diff = float(shoot - deploy)
        out = float(diff / 3)
        return out
    else:
        return 1

def dbadd_entry(nick, chan, db, conn, shoot, friend):
    """Takes care of adding a new row to the database."""
    query = table.insert().values(
        network = conn.name,
        chan = chan.lower(),
        name = nick.lower(),
        shot = shoot,
        befriend = friend)
    db.execute(query)
    db.commit()

def dbupdate(nick, chan, db, conn, shoot, friend):
    """update a db row"""
    if shoot and not friend:
        query = table.update() \
            .where(table.c.network == conn.name) \
            .where(table.c.chan == chan.lower()) \
            .where(table.c.name == nick.lower()) \
            .values(shot = shoot)
        db.execute(query)
        db.commit()
    elif friend and not shoot:
        query = table.update() \
            .where(table.c.network == conn.name) \
            .where(table.c.chan == chan.lower()) \
            .where(table.c.name == nick.lower()) \
            .values(befriend = friend)
        db.execute(query)
        db.commit()

@hook.command("bang", autohelp=False)
def bang(nick, chan, message, db, conn):
    """when there is a duck on the loose use this command to shoot it."""
    global game_status, scripters
    if chan in opt_out:
        return
    network = conn.name
    score = ""
    out = ""
    miss = ["WHOOSH! You missed the duck completely!", "Your gun jammed!", "Better luck next time."]
    if not game_status[network][chan]['game_on']:
        return "There is no activehunt right now. Use .starthunt to start a game."
    elif game_status[network][chan]['duck_status'] != 1:
        if game_status[network][chan]['no_duck_kick'] == 1:
            out = "KICK {} {} There is no duck! What are you shooting at?".format(chan, nick)
            conn.send(out)
            return
        return "There is no duck. What are you shooting at?"
    else: 
        game_status[network][chan]['shoot_time'] = time()
        deploy = game_status[network][chan]['duck_time']
        shoot = game_status[network][chan]['shoot_time']
        if nick.lower() in scripters:
            if scripters[nick.lower()] > shoot:
                return "You are in a cool down period, you can try again in {} seconds.".format(str(scripters[nick.lower()] - shoot))
        chance = hit_or_miss(deploy, shoot)
        if not random.random() <= chance and chance > .05:
            out = random.choice(miss) + " You can try again in 7 seconds."
            scripters[nick.lower()] = shoot + 7 
            return out
        if chance == .05:
            out += "You pulled the trigger in {} seconds, that's mighty fast. Are you sure you aren't a script? Take a 2 hour cool down.".format(str(shoot - deploy))
            scripters[nick.lower()] = shoot + 7200
            if not random.random() <= chance:
                return random.choice(miss) + " " + out
            else:
                message(out)
        game_status[network][chan]['duck_status'] = 2
        score = db.execute(select([table.c.shot]) \
            .where(table.c.network == conn.name) \
            .where(table.c.chan == chan.lower()) \
            .where(table.c.name == nick.lower())).fetchone()
        if score:
            score = score[0]
            score += 1
            dbupdate(nick, chan, db, conn, score, 0)
        else:
            score = 1
            dbadd_entry(nick, chan, db, conn, score, 0)
        duck = "duck" if score == 1 else "ducks"
        message("{} you shot a duck! You have killed {} {} in {}.".format(nick,score, duck, chan))
        set_ducktime(chan, conn)

@hook.command("befriend", autohelp=False)
def befriend(nick, chan, message, db, conn):
    """when there is a duck on the loose use this command to befriend it before someone else shoots it."""
    global game_status, scripters
    if chan in opt_out:
        return
    network = conn.name
    out = ""
    score = ""
    miss = ["The duck didn't want to be friends, maybe next time.", "Well this is awkard, the duck needs to think about it.", "The duck said no, maybe bribe it with some pizza? Ducks love pizza don't they?", "Who knew ducks could be so picky?"]
    if not game_status[network][chan]['game_on']:
        return "There is no hunt right now. Use .starthunt to start a game."
    elif game_status[network][chan]['duck_status'] != 1:
        if game_status[network][chan]['no_duck_kick'] == 1:
            out = "KICK {} {} You tried befriending a non-existent duck, that's fucking creepy.".format(chan, nick)
            conn.send(out)
            return
        return "You tried befriending a non-existent duck, that's fucking creepy."
    else:
        game_status[network][chan]['shoot_time'] = time()
        deploy = game_status[network][chan]['duck_time']
        shoot = game_status[network][chan]['shoot_time']
        if nick.lower() in scripters:
            if scripters[nick.lower()] > shoot:
                return "You are in a cool down period, you can try again in {} seconds.".format(str(scripters[nick.lower()] - shoot))
        chance = hit_or_miss(deploy, shoot)
        if not random.random() <= chance and chance > .05:
            out = random.choice(miss) + " You can try again in 7 seconds."
            scripters[nick.lower()] = shoot + 7
            return out
        if chance == .05:
            out += "You tried friending that duck in {} seconds, that's mighty fast. Are you sure you aren't a script? Take a 2 hour cool down.".format(str(shoot - deploy))
            scripters[nick.lower()] = shoot + 7200
            if not random.random() <= chance:
                return random.choice(miss) + " " + out
            else:
                message(out)

        game_status[network][chan]['duck_status'] = 2
        score = db.execute(select([table.c.befriend]) \
            .where(table.c.network == conn.name) \
            .where(table.c.chan == chan.lower()) \
            .where(table.c.name == nick.lower())).fetchone()
        if score:
            score = score[0]
            score += 1
            dbupdate(nick, chan, db, conn, 0, score)
        else:
            score = 1
            dbadd_entry(nick, chan, db, conn, 0, score)
        duck = "duck" if score == 1 else "ducks"
        message("{} you befriended a duck! You have made friends with {} {} in {}.".format(nick,score, duck, chan))
        set_ducktime(chan,conn)

def smart_truncate(content, length=320, suffix='...'):
    if len(content) <= length:
        return content
    else:
        return content[:length].rsplit(' • ', 1)[0]+suffix


@hook.command("friends", autohelp=False)
def friends(text, chan, conn, db):
    """Prints a list of the top duck friends in the channel, if 'global' is specified all channels in the database are included."""
    if chan in opt_out:
        return
    friends = defaultdict(int)
    out = ""
    if text.lower() == 'global':
        out = "Duck friend scores across the network: "
        scores = db.execute(select([table.c.name, table.c.befriend]) \
            .where(table.c.network == conn.name) \
            .order_by(desc(table.c.befriend)))
        if scores:    
            for row in scores:
                if row[1] == 0:
                    continue
                friends[row[0]] += row[1]
        else:
            return "it appears no on has friended any ducks yet."
    else:
        out = "Duck friend scores in {}: ".format(chan)
        scores = db.execute(select([table.c.name, table.c.befriend]) \
            .where(table.c.network == conn.name) \
            .where(table.c.chan == chan.lower()) \
            .order_by(desc(table.c.befriend)))
        if scores:
            for row in scores:
                if row[1] == 0:
                    continue
                friends[row[0]] += row[1]
        else:
            return "it appears no on has friended any ducks yet."

    topfriends = sorted(friends.items(), key=operator.itemgetter(1), reverse = True)
    out += ' • '.join(["{}: {}".format('\x02' + k[:1] + u'\u200b' + k[1:] + '\x02', str(v))  for k, v in topfriends])
    out = smart_truncate(out)
    return out

@hook.command("killers", autohelp=False)
def killers(text, chan, conn, db):
    """Prints a list of the top duck killers in the channel, if 'global' is specified all channels in the database are included."""
    if chan in opt_out:
        return
    killers = defaultdict(int)
    out = ""
    if text.lower() == 'global':
        out = "Duck killer scores across the network: "
        scores = db.execute(select([table.c.name, table.c.shot]) \
            .where(table.c.network == conn.name) \
            .order_by(desc(table.c.shot)))
        if scores:
            for row in scores:
                if row[1] == 0:
                    continue
                killers[row[0]] += row[1]
        else:
            return "it appears no on has killed any ducks yet."
    else:
        out = "Duck killer scores in {}: ".format(chan)
        scores = db.execute(select([table.c.name, table.c.shot]) \
            .where(table.c.network == conn.name) \
            .where(table.c.chan == chan.lower()) \
            .order_by(desc(table.c.shot)))
        if scores:
            for row in scores:
                if row[1] == 0:
                    continue
                killers[row[0]] += row[1]
        else:
            return "it appears no on has killed any ducks yet."

    topkillers = sorted(killers.items(), key=operator.itemgetter(1), reverse = True)
    out += ' • '.join(["{}: {}".format('\x02' + k[:1] + u'\u200b' + k[1:] + '\x02', str(v))  for k, v in topkillers])
    out = smart_truncate(out)
    return out

@hook.command("duckforgive", permissions=["op", "ignore"])
def duckforgive(text):
    """Allows people to be removed from the mandatory cooldown period."""
    global scripters
    if text.lower() in scripters and scripters[text.lower()] > time():
        scripters[text.lower()] = 0
        return "{} has been removed from the mandatory cooldown period.".text()
    else:
        return "I couldn't find anyone banned from the hunt by that nick"
