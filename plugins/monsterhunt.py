import random
import re
import operator
import json

from time import time
from collections import defaultdict
from sqlalchemy import Table, Column, String, Integer, PrimaryKeyConstraint, desc
from sqlalchemy.sql import select
from cloudbot import hook
from cloudbot.event import EventType
from cloudbot.util import database
from cloudbot.util import web

duck = [" ε=ε=ε=ε=ε=┌(；　・＿・)┘ ", " ε=ε=ε=ε=ε=ε=┌(๑ʘ∀ʘ)┘ ", " ===≡≡≡｡ﾟ┌(ﾟ´Д`ﾟ)┘ﾟ｡ ", " ・・・・・・・ᕕ(╯°□°)ᕗ " ]
duck_tail = ["[¬º-°]¬", "(▼皿▼)", "←~∋(｡Ψ▼ｰ▼)∈", "∋━━o(｀∀´oメ）～→", "(˼●̙̂ ̟ ̟̎ ̟ ̘●̂˻)", "(;´༎ຶД༎ຶ`)", "(((༼•̫͡•༽)))"]
duck_noise = ["RUN!!!!!", "AHHHHHHHHHHH", "FFFFFUUUUUUU!"]

table = Table(
    'monster_hunt',
    database.metadata,
    Column('network', String),
    Column('name', String),
    Column('shot', Integer),
    Column('befriend', Integer),
    Column('chan', String),
    PrimaryKeyConstraint('name', 'chan','network')
    )

optout = Table(
    'monster_nohunt',
    database.metadata,
    Column('network', String),
    Column('chan', String),
    PrimaryKeyConstraint('chan','network')
    )



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


@hook.on_start()
def load_optout(db):
    """load a list of channels duckhunt should be off in. Right now I am being lazy and not
    differentiating between networks this should be cleaned up later."""
    global opt_out
    opt_out = []
    chans = db.execute(select([optout.c.chan]))
    if chans:
        for row in chans:
            chan = row["chan"]
            opt_out.append(chan)

#@hook.command("starthunt", autohelp=False)
def start_hunt(bot, chan, message, conn):
    """This command starts a spooky MONSTER hunt in your channel, to stop the hunt use .stophunt"""
    global game_status
    if chan in opt_out:
        return
    elif not chan.startswith("#"):
        return "No hunting by yourself, that isn't safe."
    check = game_status[conn.name][chan]['game_on']
    if check:
        return "There is already a hunt running in {}.".format(chan)
    #else:
    #    game_status[conn.name][chan]['game_on'] = 1
    #set_ducktime(chan, conn)
    message("Thanks for participating in the 2015 monster hunt. The monster hunt has ended. To see the highest average score use '.monsterkillers average' or '.monsterfriends average'. For more information on this creepy event see https://redd.it/3q31qw", chan)

def set_ducktime(chan, conn):
    global game_status
    game_status[conn.name][chan]['next_duck_time'] = random.randint(int(time()) + 480, int(time()) + 3600)
    #game_status[conn.name][chan]['flyaway'] = game_status[conn.name][chan]['next_duck_time'] + 600
    game_status[conn.name][chan]['duck_status'] = 0
    return

#@hook.command("stophunt", autohelp=False)
def stop_hunt(chan, conn):
    """This command stops the Monster hunt in your channel. Scores will be preserved"""
    global game_status
    if chan in opt_out:
        return
    if game_status[conn.name][chan]['game_on']:
        game_status[conn.name][chan]['game_on'] = 0
        return "The hunt has been stopped."
    else:
        return "There is no monster hunt running in {}.".format(chan)

#@hook.command("monsterkick")
def no_duck_kick(text, chan, conn, notice):
    """If the bot has OP or half-op in the channel you can specify .monsterkick enable|disable so that people are kicked for shooting or befriending a non-existent monster. Default is off."""
    global game_status
    if chan in opt_out:
        return
    if text.lower() == 'enable':
        game_status[conn.name][chan]['no_duck_kick'] = 1
        return "users will now be kicked for shooting or befriending non-existent monsters. The bot needs to have appropriate flags to be able to kick users for this to work."
    elif text.lower() == 'disable':
        game_status[conn.name][chan]['no_duck_kick'] = 0
        return "kicking for non-existent monsters has been disabled."
    else:
        notice(no_duck_kick.__doc__)
        return

def generate_duck():
    """Try and randomize the monster message so people can't highlight on it/script against it."""
    dtail = random.choice(duck_tail)
    rt = random.randint(1, len(dtail) - 1)
    dtail = dtail[:rt] + u' \u200b ' + dtail[rt:]
    dbody = random.choice(duck)
    rb = random.randint(1, len(dbody) - 1)
    dbody = dbody[:rb] + u'\u200b' + dbody[rb:]
    dnoise = random.choice(duck_noise)
    rn = random.randint(1, len(dnoise) - 1)
    dnoise = dnoise[:rn] + u'\u200b' + dnoise[rn:]
    return (dtail, dbody, dnoise)


#@hook.periodic(11, initial_interval=11)
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
            # Leave this commented out for now. I haven't decided how to make ducks leave.
            #if active == 1 and duck_status == 1 and game_status[network][chan]['flyaway'] <= int(time()):
            #    conn.message(chan, "The duck flew away.")
            #    game_status[network][chan]['duck_status'] = 2
            #    set_ducktime(chan, conn)
            continue
        continue


def hit_or_miss(deploy, shoot):
    """This function calculates if the befriend or bang will be successful."""
    if shoot - deploy < 1:
        return .05
    elif 1 <= shoot - deploy <= 7:
        out = random.uniform(.60, .75)
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
    elif friend and shoot:
        query = table.update() \
            .where(table.c.network == conn.name) \
            .where(table.c.chan == chan.lower()) \
            .where(table.c.name == nick.lower()) \
            .values(befriend = friend) \
            .values(shot = shoot)
        db.execute(query)
        db.commit()

#@hook.command("bang", autohelp=False)
def bang(nick, chan, message, db, conn, notice):
    """when there is a monster chasing someone use this command to shoot it."""
    global game_status, scripters
    if chan in opt_out:
        return
    network = conn.name
    score = ""
    out = ""
    miss = ["WHOOSH! You totally missed the monster. Save the poor human!", "Your gun jammed!", "Better luck next time.", "Good thing this is just an IRC game cus your aim is terrible!" ]
    if not game_status[network][chan]['game_on']:
        return "There is no activehunt right now. Use .starthunt to start a game."
    elif game_status[network][chan]['duck_status'] != 1:
        if game_status[network][chan]['no_duck_kick'] == 1:
            out = "KICK {} {} There is no monster! What are you shooting at?".format(chan, nick)
            conn.send(out)
            return
        return "There is no monster. What are you shooting at?"
    else: 
        game_status[network][chan]['shoot_time'] = time()
        deploy = game_status[network][chan]['duck_time']
        shoot = game_status[network][chan]['shoot_time']
        if nick.lower() in scripters:
            if scripters[nick.lower()] > shoot:
                notice("You are in a cool down period, you can try again in {} seconds.".format(str(scripters[nick.lower()] - shoot)))
                return
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
        timer = "{:.3f}".format(shoot - deploy)
        duck = "monster" if score == 1 else "monsters"
        message("{} you shot a monster and saved a human in {} seconds! You have killed {} {} in {}.".format(nick, timer, score, duck, chan))
        set_ducktime(chan, conn)

#@hook.command("befriend", autohelp=False)
def befriend(nick, chan, message, db, conn, notice):
    """when there is a monster on the loose chasing a human use this command to befriend it before someone else shoots it. This will also let it kill the human."""
    global game_status, scripters
    if chan in opt_out:
        return
    network = conn.name
    out = ""
    score = ""
    miss = ["The monster didn't want to be friends, you are lucky they didn't eat you too!", "The monster just grunted and kept chasing his prey, maybe you should provide an offering of some kind", "Maybe your breath smells too sweet or your face looks too nice. Either way the monster rejected you."]
    if not game_status[network][chan]['game_on']:
        return "There is no hunt right now. Use .starthunt to start a game."
    elif game_status[network][chan]['duck_status'] != 1:
        if game_status[network][chan]['no_duck_kick'] == 1:
            out = "KICK {} {} You tried befriending a non-existent monster, that's fucking creepy.".format(chan, nick)
            conn.send(out)
            return
        return "You tried befriending a non-existent monster, that's fucking creepy."
    else:
        game_status[network][chan]['shoot_time'] = time()
        deploy = game_status[network][chan]['duck_time']
        shoot = game_status[network][chan]['shoot_time']
        if nick.lower() in scripters:
            if scripters[nick.lower()] > shoot:
                notice("You are in a cool down period, you can try again in {} seconds.".format(str(scripters[nick.lower()] - shoot)))
                return
        chance = hit_or_miss(deploy, shoot)
        if not random.random() <= chance and chance > .05:
            out = random.choice(miss) + " You can try again in 7 seconds."
            scripters[nick.lower()] = shoot + 7
            return out
        if chance == .05:
            out += "You tried friending that monster in {} seconds, that's mighty fast. Are you sure you aren't a script? Take a 2 hour cool down.".format(str(shoot - deploy))
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
        duck = "monster" if score == 1 else "monsters"
        timer = "{:.3f}".format(shoot - deploy)
        message("{} you befriended a monster in {} seconds! You have made friends with {} {} in {}.".format(nick, timer, score, duck, chan))
        set_ducktime(chan,conn)

def smart_truncate(content, length=320, suffix='...'):
    if len(content) <= length:
        return content
    else:
        return content[:length].rsplit(' • ', 1)[0]+suffix


@hook.command("monsterfriends", autohelp=False)
def friends(text, chan, conn, db):
    """Prints a list of the top monster friends in the channel, if 'global' is specified all channels in the database are included."""
    if chan in opt_out:
        return
    friends = defaultdict(int)
    chancount = defaultdict(int)
    out = ""
    if text.lower() == 'global' or text.lower() == 'average':
        out = "Monster friend scores across the network: "
        scores = db.execute(select([table.c.name, table.c.befriend]) \
            .where(table.c.network == conn.name) \
            .order_by(desc(table.c.befriend)))
        if scores:    
            for row in scores:
                if row[1] == 0:
                    continue
                chancount[row[0]] += 1
                friends[row[0]] += row[1]
            if text.lower() == 'average':
                for k, v in friends.items():
                    friends[k] = int(v / chancount[k])
        else:
            return "it appears no one has friended any monsters yet."
    else:
        out = "Monster friend scores in {}: ".format(chan)
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
            return "it appears no one has friended any monsters yet."

    topfriends = sorted(friends.items(), key=operator.itemgetter(1), reverse = True)
    url = web.paste(json.dumps(topfriends, indent=4))
    out += ' • '.join(["{}: {}".format('\x02' + k[:1] + u'\u200b' + k[1:] + '\x02', str(v))  for k, v in topfriends])
    out = smart_truncate(out)
    out += " " + url
    return out

@hook.command("monsterkillers", autohelp=False)
def killers(text, chan, conn, db):
    """Prints a list of the top monster killers in the channel, if 'global' is specified all channels in the database are included."""
    if chan in opt_out:
        return
    killers = defaultdict(int)
    chancount = defaultdict(int)
    out = ""
    if text.lower() == 'global' or text.lower() == 'average':
        out = "Monster killer scores across the network: "
        scores = db.execute(select([table.c.name, table.c.shot]) \
            .where(table.c.network == conn.name) \
            .order_by(desc(table.c.shot)))
        if scores:
            for row in scores:
                if row[1] == 0:
                    continue
                chancount[row[0]] += 1
                killers[row[0]] += row[1]
            if text.lower() == 'average':
                for k, v in killers.items():
                    killers[k] = int(v / chancount[k])
        else:
            return "it appears no one has killed any monsters yet."
    else:
        out = "Monster killer scores in {}: ".format(chan)
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
            return "it appears no on has killed any monsters yet."

    topkillers = sorted(killers.items(), key=operator.itemgetter(1), reverse = True)
    url = web.paste(json.dumps(topkillers, indent=4))
    out += ' • '.join(["{}: {}".format('\x02' + k[:1] + u'\u200b' + k[1:] + '\x02', str(v))  for k, v in topkillers])
    out = smart_truncate(out) + " " + url
    return out

#@hook.command("monsterforgive", permissions=["op", "ignore"])
def duckforgive(text):
    """Allows people to be removed from the mandatory cooldown period."""
    global scripters
    if text.lower() in scripters and scripters[text.lower()] > time():
        scripters[text.lower()] = 0
        return "{} has been removed from the mandatory cooldown period.".format(text)
    else:
        return "I couldn't find anyone banned from the hunt by that nick"

#@hook.command("hunt_opt_out", permissions=["op", "ignore"], autohelp=False)
def hunt_opt_out(text, chan, db, conn):
    """Running this command without any arguments displays the status of the current channel. hunt_opt_out add #channel will disable all duck and monster hunt commands in the specified channel. hunt_opt_out remove #channel will re-enable the game for the specified channel."""
    if not text:
        if chan in opt_out:
            return "Monster hunt is disabled in {}. To re-enable it run .hunt_opt_out remove #channel".format(chan)
        else:
            return "Monster hunt is enabled in {}. To disable it run .hunt_opt_out add #channel".format(chan)
    if text == "list":
        return ", ".join(opt_out)
    if len(text.split(' ')) < 2:
        return "please specify add or remove and a valid channel name"
    command = text.split()[0]
    channel = text.split()[1]
    if not channel.startswith('#'):
        return "Please specify a valid channel."
    if command.lower() == "add":
        if channel in opt_out:
            return "Monster hunt has already been disabled in {}.".format(channel)
        query = optout.insert().values(
            network = conn.name,
            chan = channel.lower())
        db.execute(query)
        db.commit()
        load_optout(db)
        return "The monster hunt has been successfully disabled in {}.".format(channel)
    if command.lower() == "remove":
        if not channel in opt_out:
            return "Monster hunt is already enabled in {}.".format(channel)
        delete = optout.delete(optout.c.chan == channel.lower())
        db.execute(delete)
        db.commit()
        load_optout(db)

@hook.command("monstermerge", permissions=["botcontrol"])
def duck_merge(text, conn, db, message):
    """Moves the monster scores from one nick to another nick. Accepts two nicks as input the first will have their monster scores removed the second will have the first score added. Warning this cannot be undone."""
    oldnick, newnick = text.lower().split()
    if oldnick == newnick:
        return "please specify two different nicks."
    if not oldnick or not newnick:
        return "Please specify two nicks for this command."
    oldnickscore = db.execute(select([table.c.name, table.c.chan, table.c.shot, table.c.befriend])
        .where(table.c.network == conn.name)
        .where(table.c.name == oldnick)).fetchall()
    newnickscore = db.execute(select([table.c.name, table.c.chan, table.c.shot, table.c.befriend])
        .where(table.c.network == conn.name)
        .where(table.c.name == newnick)).fetchall()
    duckmerge = defaultdict(lambda: defaultdict(int))
    duckmerge["TKILLS"] = 0
    duckmerge["TFRIENDS"] = 0
    channelkey = {"update":[], "insert":[]}
    if oldnickscore:
        if newnickscore:
            for row in newnickscore:
                duckmerge[row["chan"]]["shot"] = row["shot"]
                duckmerge[row["chan"]]["befriend"] = row["befriend"]
            for row in oldnickscore:
                if row["chan"] in duckmerge:
                    duckmerge[row["chan"]]["shot"] = duckmerge[row["chan"]]["shot"] + row["shot"]
                    duckmerge[row["chan"]]["befriend"] = duckmerge[row["chan"]]["befriend"] + row["befriend"]
                    channelkey["update"].append(row["chan"])
                    duckmerge["TKILLS"] = duckmerge["TKILLS"] + row["shot"]
                    duckmerge["TFRIENDS"] = duckmerge["TFRIENDS"] + row["befriend"]
                else:
                    duckmerge[row["chan"]]["shot"] = row["shot"]
                    duckmerge[row["chan"]]["befriend"] = row["befriend"]
                    channelkey["insert"].append(row["chan"])
                    duckmerge["TKILLS"] = duckmerge["TKILLS"] + row["shot"]
                    duckmerge["TFRIENDS"] = duckmerge["TFRIENDS"] + row["befriend"]
        else:
            for row in oldnickscore:
                duckmerge[row["chan"]]["shot"] = row["shot"]
                duckmerge[row["chan"]]["befriend"] = row["befriend"]
                channelkey["insert"].append(row["chan"])
       # TODO: Call dbupdate() and db_add_entry for the items in duckmerge
        for channel in channelkey["insert"]:
            dbadd_entry(newnick, channel, db, conn, duckmerge[channel]["shot"], duckmerge[channel]["befriend"])
        for channel in channelkey["update"]:
            dbupdate(newnick, channel, db, conn, duckmerge[channel]["shot"], duckmerge[channel]["befriend"])
        query = table.delete() \
            .where(table.c.network == conn.name) \
            .where(table.c.name == oldnick)
        db.execute(query)
        db.commit()
        message("Migrated {} monster kills and {} monster friends from {} to {}".format(duckmerge["TKILLS"], duckmerge["TFRIENDS"], oldnick, newnick))
    else:
        return "There are no monster scores to migrate from {}".format(oldnick)

@hook.command("monsters", autohelp=False)
def ducks_user(text, nick, chan, conn, db, message):
    """Prints a users monster stats. If no nick is input it will check the calling username."""
    name = nick.lower()
    if text:
        name = text.split()[0].lower()
    ducks = defaultdict(int)
    scores = db.execute(select([table.c.name, table.c.chan, table.c.shot, table.c.befriend])
        .where(table.c.network == conn.name)
        .where(table.c.name == name)).fetchall()
    if scores:
        for row in scores:
            if row["chan"].lower() == chan.lower():
                ducks["chankilled"] += row["shot"]
                ducks["chanfriends"] += row["befriend"]
            ducks["killed"] += row["shot"]
            ducks["friend"] += row["befriend"]
            ducks["chans"] += 1
        if ducks["chans"] == 1:
            message("{} has killed {} and befriended {} monsters in {}.".format(name, ducks["chankilled"], ducks["chanfriends"], chan))
            return
        kill_average = int(ducks["killed"] / ducks["chans"])
        friend_average = int(ducks["friend"] / ducks["chans"])
        message("\x02{}'s\x02 duck stats: \x02{}\x02 killed and \x02{}\x02 befriended in {}. Across {} channels: \x02{}\x02 killed and \x02{}\x02 befriended. Averaging \x02{}\x02 kills and \x02{}\x02 friends per channel.".format(name, ducks["chankilled"], ducks["chanfriends"], chan, ducks["chans"], ducks["killed"], ducks["friend"], kill_average, friend_average))
    else:
        return "It appears {} has not participated in the monster hunt.".format(name)

@hook.command("monsterstats", autohelp=False)
def duck_stats(chan, conn, db, message):
    """Prints monster statistics for the entire channel and totals for the network."""
    ducks = defaultdict(int)
    scores = db.execute(select([table.c.name, table.c.chan, table.c.shot, table.c.befriend])
        .where(table.c.network == conn.name)).fetchall()
    if scores:
        ducks["friendchan"] = defaultdict(int)
        ducks["killchan"] = defaultdict(int)
        for row in scores:
            ducks["friendchan"][row["chan"]] += row["befriend"]
            ducks["killchan"][row["chan"]] += row["shot"]
            #ducks["chans"] += 1
            if row["chan"].lower() == chan.lower():
                ducks["chankilled"] += row["shot"]
                ducks["chanfriends"] += row["befriend"]
            ducks["killed"] += row["shot"]
            ducks["friend"] += row["befriend"]
        ducks["chans"] = int((len(ducks["friendchan"]) + len(ducks["killchan"])) / 2)
        killerchan, killscore = sorted(ducks["killchan"].items(), key=operator.itemgetter(1), reverse = True)[0]
        friendchan, friendscore = sorted(ducks["friendchan"].items(), key=operator.itemgetter(1), reverse =True)[0]
        message("\x02Monster Stats:\x02 {} killed and {} befriended in \x02{}\x02. Across {} channels \x02{}\x02 monsters have been killed and \x02{}\x02 befriended. \x02Top Channels:\x02 \x02{}\x02 with {} kills and \x02{}\x02 with {} friends".format(ducks["chankilled"], ducks["chanfriends"], chan, ducks["chans"], ducks["killed"], ducks["friend"], killerchan, killscore, friendchan, friendscore))
    else:
        return "It looks like there has been no monster activity on this channel or network."
