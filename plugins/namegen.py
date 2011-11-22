from util import hook,molecular
import unicodedata

@hook.command()
def namegen(inp, say = None, nick = None, input=None, notice=None):
    ".namegen [modules] -- generates some names using the chosen modules. \".namegen list\" will display a list of all modules"
    gen = molecular.Molecule()

    all_modules = ["dever_f", "dwarves", "elves_m", "fantasy", "harn_cln", "harn_gar", "harn_m2", " harn_s_m", "human_m", "narn", "dever_m", "elves_d", "elves_n", "felana", " harn_f2", "harn_k_f", "harn_m", "hobbits", "inns", " orcs_t", "dragon", "elves_f", "elves_t", "general", "harn_f", "harn_k_m", "harn_s_f", "human_f", "items", "orcs_wh"]

    modules = []

    if inp == "list":
        notice("Available modules: dever_f, dwarves, elves_m, fantasy, harn_cln, harn_gar, harn_m2,  harn_s_m, human_m, narn, dever_m, elves_d, elves_n, felana, harn_f2, harn_k_f, harn_m,   hobbits, inns, orcs_t, dragon, elves_f, elves_t, general, harn_f, harn_k_m, harn_s_f, human_f, items, orcs_wh")
        return

    if inp:
        modules = inp.split(' ')
    else:
        modules = ["human_m", "human_f"]

    for module in modules:
        if module in all_modules:
            gen.load(module.encode('ascii'))

    if not gen.name():
        return "No valid modules specified :("

    message = "Here are some names: "
    for i in range(6):
        message += gen.name() + ", "

    return message
