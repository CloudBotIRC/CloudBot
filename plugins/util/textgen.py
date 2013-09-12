import re
import random

TEMPLATE_RE = re.compile(r"\{(.+?)\}")


class TextGenerator(object):
    def __init__(self, name, templates, default_templates, parts, variables=None):
        self.name = name
        self.templates = templates
        self.default_templates = default_templates
        self.parts = parts
        self.variables = variables

    def generate_string(self, template=None):
        """
        Generates one string using the specified templates.
        If no templates are specified, use a random template from the default_templates list.
        """
        text = self.templates[template or random.choice(self.default_templates)]

        # get a list of all text parts we need
        required_parts = TEMPLATE_RE.findall(text)

        for required_part in required_parts:
            part = random.choice(self.parts[required_part])
            text = text.replace("{%s}" % required_part, part)

        return text

    def generate_strings(self, amount, template=None):
        strings = []
        for i in xrange(amount):
            strings.append(self.generate_string())
        return strings

    def get_template(self, template):
        return self.templates[template]