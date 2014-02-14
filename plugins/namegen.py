import json
import os

from util import hook, text, textgen


GEN_DIR = "./plugins/data/name_files/"


def get_generator(_json):
    data = json.loads(_json)
    return textgen.TextGenerator(data["templates"],
                                 data["parts"], default_templates=data["default_templates"])


@hook.command(autohelp=False)
def namegen(inp, notice=None):
    """namegen [generator] -- Generates some names using the chosen generator.
    'namegen list' will display a list of all generators."""

    # clean up the input
    inp = inp.strip().lower()

    # get a list of available name generators
    files = os.listdir(GEN_DIR)
    all_modules = []
    for i in files:
        if os.path.splitext(i)[1] == ".json":
            all_modules.append(os.path.splitext(i)[0])
    all_modules.sort()

    # command to return a list of all available generators
    if inp == "list":
        message = "Available generators: "
        message += text.get_text_list(all_modules, 'and')
        notice(message)
        return

    if inp:
        selected_module = inp.split()[0]
    else:
        # make some generic fantasy names
        selected_module = "fantasy"

    # check if the selected module is valid
    if not selected_module in all_modules:
        return "Invalid name generator :("

    # load the name generator
    with open(os.path.join(GEN_DIR, "{}.json".format(selected_module))) as f:
        try:
            generator = get_generator(f.read())
        except ValueError as error:
            return "Unable to read name file: {}".format(error)

    # time to generate some names
    name_list = generator.generate_strings(10)

    # and finally return the final message :D
    return "Some names to ponder: {}.".format(text.get_text_list(name_list, 'and'))
