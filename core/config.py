import json
import os


class Config(dict):
    def __init__(self, name, *args, **kwargs):
        self.path = os.path.abspath("{}.json".format(name))
        self.update(*args, **kwargs)

    def load_config(self):
        with open(self.path) as f:
            self.update(json.load(f))


    def save_config(self):
        pass