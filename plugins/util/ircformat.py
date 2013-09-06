def bb(format_string):
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
    '[lgray]':'\x0315',}
    stuff['style'] = {'[b]':'\x02'}
    stuff['sym'] = {'[point]':'\x07'}
    final = {}
    for x in stuff:
        final.update(x)
    for x in final:
        format_string = format_string.replace(x,rep[x])
    return format_string
