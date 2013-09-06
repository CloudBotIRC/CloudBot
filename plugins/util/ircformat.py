def bb(format_string):
    rep = {'[b]':'\x02',
    '[White]':'\x030',
    '[Black]':'\x031',
    '[dBlue]':'\x032',
    '[dGreen]':'\x033',
    '[dRed]':'\x034',
    '[Brown]':'\x035',
    '[Purple]':'\x036',
    '[Gold]':'\x037',
    'Yellow':'\x038',
    '[Green]':'\x039',
    '[Cyan]':'\x0310',
    '[lBlue]':'\x0311',
    '[Blue]':'\x0312',
    '[Pink]':'\x0313',
    '[Gray]':'\x0314',
    '[lGray]':'\x0315',}
    for x in rep:
        format_string = format_string.replace(x,rep[x])
    return format_string
