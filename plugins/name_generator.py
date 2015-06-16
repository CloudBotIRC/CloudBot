"""
name_generator.py

Generates fun names using the textgen module.

Created By:
    - Luke Rogers <https://github.com/lukeroge>

License:
    GPL v3
"""

import json
import codecs
import os

from cloudbot import hook
from cloudbot.util import formatting, textgen


def get_generator(_json):
    data = json.loads(_json)
    return textgen.TextGenerator(data["templates"],
                                 data["parts"], default_templates=data["default_templates"])


@hook.command(autohelp=False)
def namegen(text, bot, notice):
    """[generator|list] - generates some names using the chosen generator, or lists all generators if 'list' is specified
    :type bot: cloudbot.bot.CloudBot
    """

    # clean up the input
    inp = text.strip().lower()

    # get a list of available name generators
    files = os.listdir(os.path.join(bot.data_dir, "name_files"))
    all_modules = [os.path.splitext(i)[0] for i in files if os.path.splitext(i)[1] == ".json"]
    all_modules.sort()

    # command to return a list of all available generators
    if inp == "list":
        message = "Available generators: "
        message += formatting.get_text_list(all_modules, 'and')
        notice(message)
        return

    if inp:
        selected_module = inp.split()[0]
    else:
        # make some generic fantasy names
        selected_module = "fantasy"

    # check if the selected module is valid
    if selected_module not in all_modules:
        return "{} is not a valid name generator.".format(inp)

    # load the name generator
    path = os.path.join(bot.data_dir, "name_files", "{}.json".format(selected_module))

    with codecs.open(path, encoding="utf-8") as f:
        try:
            generator = get_generator(f.read())
        except ValueError as error:
            return "Unable to read name file: {}".format(error)

    # time to generate some names
    name_list = generator.generate_strings(10)

    # and finally return the final message :D
    return "Some names to ponder: {}.".format(formatting.get_text_list(name_list, 'and'))
