import re
import random

TEMPLATE_RE = re.compile(r"\{(.+?)\}")


class TextGenerator(object):
    def __init__(self, templates, parts, default_templates=None, variables=None):
        self.templates = templates
        self.default_templates = default_templates
        self.parts = parts
        self.variables = variables

    def generate_string(self, template=None):
        """
        Generates one string using the specified templates.
        If no templates are specified, use a random template from the default_templates list.
        """
        if self.default_templates:
            text = self.templates[template or random.choice(self.default_templates)]
        else:
            text = random.choice(self.templates)

        # replace static variables in the template with provided values
        if self.variables:
            for key, value in list(self.variables.items()):
                text = text.replace("{%s}" % key, value)

        # get a list of all text parts we need
        required_parts = TEMPLATE_RE.findall(text)

        for required_part in required_parts:
            _parts = self.parts[required_part]

            # I kept this check here for some weird reason I long forgot
            if isinstance(_parts, str):
                part = _parts
            else:
                _weighted_parts = []

                # this uses way too much code, but I wrote it at like 6am
                for _part in _parts:
                    if isinstance(_part, list):
                        __part, __weight = _part
                        _weighted_parts.append((__part, __weight))
                    else:
                        __part = _part
                        _weighted_parts.append((__part, 5))

                population = [val for val, cnt in _weighted_parts for i in range(cnt)]
                part = random.choice(population)

            text = text.replace("{%s}" % required_part, part)

        return text

    def generate_strings(self, amount):
        strings = []
        for i in range(amount):
            strings.append(self.generate_string())
        return strings

    def get_template(self, template):
        return self.templates[template]
