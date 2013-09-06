def raw(format_string):
    """Replace based irc formatting"""
    stuff = {}
    stuff['col'] = {'[white]':'\x030',
    '[black]':'\x031',
    '[dblue]':'\x032',
    '[dgreen]':'\x033',
    '[dred]':'\x034',
    '[brown]':'\x035',
    '[purple]':'\x036',
    '[gold]':'\x037',
    '[yellow]':'\x038',
    '[green]':'\x039',
    '[cyan]':'\x0310',
    '[lblue]':'\x0311',
    '[blue]':'\x0312',
    '[pink]':'\x0313',
    '[gray]':'\x0314',
    '[lgray]':'\x0315',
    '[err]':'\x034\x02'
    '[/err]':'\x030\x02'}
    stuff['style'] = {'[b]':'\x02',
                      '[clear]':'\x0f'}
    stuff['sym'] = {'[point]':'\x07'}
    stuff['text'] = {'[url]':'http://'}
    final = {}
    for x in stuff:
        final.update(stuff[x])
    for x in final:
        format_string = format_string.replace(x,final[x])
    return format_string
def err(format_string):
    """Format the string with standard error styling"""
    return "\x034\x02{}\x0f".format(format_string)