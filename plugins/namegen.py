# Plugin by Lukeroge
from util import hook
from util import molecular
from util.text import get_text_list


@hook.command(autohelp=False)
def namegen(inp, notice=None):
    ".namegen [modules] -- Generates some names using the chosen modules. " \
    "'.namegen list' will display a list of all modules."

    gen = molecular.Molecule()

    # get a list of available modules
    all_modules = gen.list_modules()

    # command to return a list of all available modules
    if inp == "list":
        message = "Available modules: "
        message += get_text_list(all_modules, 'and')
        notice(message)
        return

    if inp:
        # split the input into a list of modules
        selected_modules = inp.split(' ')
    else:
        # make some generic fantasy names
        selected_modules = ["fantasy"]

    # loop over the "selected_modules" list, and load any valid modules
    for module in selected_modules:
        if module in all_modules:
            gen.load(module.encode('ascii'))

    # lets try making a name to see if any modules actually got loaded
    if not gen.name():
        return "No valid modules specified :("

    # time to generate some names and put them in a list
    name_list = []
    for i in xrange(10):
        name_list.append(gen.name())

    # and finally return the final message :D
    return "Some names to ponder: %s." % get_text_list(name_list, 'and')
