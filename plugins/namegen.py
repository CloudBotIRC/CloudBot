# Plugin by Lukeroge
from util import hook
from util import molecular
import unicodedata


@hook.command()
def namegen(inp, say=None, nick=None, input=None, notice=None):
    ".namegen [modules] -- Generates some names using the chosen modules. '.namegen list' will display a list of all modules."

    gen = molecular.Molecule()

    all_modules = gen.list_modules()  # get a list of available name files

    # return a list of all available modules
    if inp == "list":
        message = "Available modules: "
        message += ', '.join(map(str, all_modules))
        notice(message)
        return

    modules = []

    selected_modules = inp.split(' ')  # split the input into a list of modules

    for module in selected_modules:  # loop over the "selected_modules" list, and load any valid modules
        if module in all_modules:
            gen.load(module.encode('ascii'))

    if not gen.name():  # lets try making a name to see if any modules actually got loaded
        return "No valid modules specified :("

    # time to generate some names and put them in a list
    name_list = []
    for i in range(8):
        name_list.append(gen.name())

    # and finally render the final message :D
    message = "Here are some names: "
    message += ', '.join(map(str, name_list))

    return message
