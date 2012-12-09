# Plugin by Lukeroge
from util import hook
from util.text import get_text_list
import json, random, re, os

TEMPLATE_RE = re.compile(r"\{(.+?)\}")
GEN_DIR = "./plugins/data/name_files/"


def get_generator(_json):
    data = json.loads(_json)
    return NameGenerator(data["name"], data["templates"],
        data["default_templates"], data["parts"])


class NameGenerator(object):
    def __init__(self, name, templates, default_templates, parts):
        self.name = name
        self.templates = templates
        self.default_templates = default_templates
        self.parts = parts

    def generate_name(self, template=None):
        """
        Generates one name using the specified templates.
        If no templates are specified, use a random template from the default_templates list.
        """
        name = self.templates[template or random.choice(self.default_templates)]

        # get a list of all name parts we need
        name_parts = TEMPLATE_RE.findall(name)

        for name_part in name_parts:
            part = random.choice(self.parts[name_part])
            name = name.replace("{%s}" % name_part, part)

        return name

    def generate_names(self, amount, template=None):
        names = []
        for i in xrange(amount):
            names.append(self.generate_name())
        return names

    def get_template(self, template):
        return self.templates[template]


@hook.command(autohelp=False)
def namegen(inp, notice=None):
    "namegen [generator] -- Generates some names using the chosen generator. " \
    "'namegen list' will display a list of all generators."

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
        message += get_text_list(all_modules, 'and')
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
    name_list = generator.generate_names(10)

    # and finally return the final message :D
    return "Some names to ponder: {}.".format(get_text_list(name_list, 'and'))
