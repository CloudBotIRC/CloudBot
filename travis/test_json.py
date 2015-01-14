"""
Travis Test file:
Test JSON files for errors.
"""

import json
import fnmatch
import codecs
import os
import sys

error = False
print("Travis: Testing all JSON files in source")

for root, dirs, files in os.walk('.'):
    for filename in fnmatch.filter(files, '*.json'):
        file = os.path.join(root, filename)
        try:
            with codecs.open(file, encoding="utf-8") as f:
                json.load(f)
            print("Travis: {} is a valid JSON file".format(file))
        except Exception as e:
            error = True
            print("Travis: {} is not a valid JSON file, json.load threw exception:\n{}".format(file, e))

if error:
    sys.exit(1)
