import json
import os


class Config(dict):
    def __init__(self, name, *args, **kwargs):
        self.path = os.path.abspath("{}.json".format(name))
        self.update(*args, **kwargs)

    def reload(self):
        with open(self.path) as f:
            self = json.load(f)
        print self


    def save(self):
        pass