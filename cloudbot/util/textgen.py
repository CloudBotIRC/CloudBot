import re
import random

import copy

TEMPLATE_RE = re.compile(r"\{(.+?)\}")


class TextGenerator(object):
    def __init__(self, templates, parts, default_templates=None, variables=None):
        self.templates = templates
        self.default_templates = default_templates
        self.parts = parts
        self.variables = variables

    def get_part(self, required_part, part_list):
        _parts = part_list[required_part]
        _weighted_parts = []
        # this uses way too much code, but I wrote it at like 6am

        for _part in _parts:
            if isinstance(_part, (list, tuple)):
                __part, __weight = _part
                _weighted_parts.append((__part, __weight))
            else:
                __part = _part
                _weighted_parts.append((__part, 5))

        population = [val for val, cnt in _weighted_parts for i in range(cnt)]
        return random.choice(population)

    def generate_string(self, template=None):
        """
        Generates one string using the specified templates.
        If no templates are specified, use a random template from the default_templates list.
        """
        if self.default_templates:
            text = self.templates[template or random.choice(self.default_templates)]
        else:
            text = random.choice(self.templates)

        # make a copy of parts for this string generation
        _parts = copy.deepcopy(self.parts)

        # replace static variables in the template with provided values
        if self.variables:
            for key, value in list(self.variables.items()):
                text = text.replace("{%s}" % key, value)

        # get a list of all text parts we need
        required_parts = TEMPLATE_RE.findall(text)

        # do magic
        for required_part in required_parts:
            # get the part
            replacement = self.get_part(required_part, _parts)

            # remove the used part
            for _part in _parts[required_part]:
                if isinstance(_part, (list, tuple)) and _part[0] == replacement:
                    _parts[required_part].remove(_part)
                elif _part == replacement:
                    _parts[required_part].remove(_part)

            text = text.replace("{%s}" % required_part, replacement, 1)

        return text

    def generate_strings(self, amount):
        strings = []
        for i in range(amount):
            strings.append(self.generate_string())
        return strings

    def get_template(self, template):
        return self.templates[template]
