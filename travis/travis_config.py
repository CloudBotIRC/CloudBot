"""
Travis Test file:
Test config.default file for JSON errors.
"""

import json
import sys


try:
    json.load(open("config.default"))
except Exception as e:
    print("Travis: 'json.load' threw exception:\n{}".format(str(e)))
    sys.exit(1)

print("Travis: config.default is a valid JSON document!")
