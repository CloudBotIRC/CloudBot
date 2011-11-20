def yaml_load(filename):
    import yaml
    fileHandle = open(filename, 'r')
    stuff = yaml.load(fileHandle.read())
    fileHandle.close()
    return stuff

def yaml_save(stuff, filename):
    import yaml
    fileHandle = open (filename, 'w' )
    fileHandle.write (yaml.dump(stuff))
    fileHandle.close()

from util import hook

@hook.event('*')
def tellinput(paraml, input=None, say=None):
#    import time
#    now = time.time()
#    spam = yaml_load('spam')
#    if spam[input.nick]:
#        spam[input.nick].append(time.time())
#    else:
#        spam[input.nick] = [time.time()]
#    for x in spam[input.nick]:
#        if now - x > 5:
#            spam[input.nick].pop(x)
#    if len(spam[input.nick]) > 8:
#        say(":O")
#        say("HOW COULD YOU "+input.nick)
#    say("lol!")
#    yaml_save(spam,'spam')
    return
