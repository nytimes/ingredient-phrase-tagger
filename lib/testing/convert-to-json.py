#!/usr/bin/env python
import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from training import utils


if len(sys.argv) < 2:
    sys.stderr.write('Usage: make-data.py FILENAME')
    sys.exit(1)

print json.dumps(utils.import_data(sys.argv[1]), indent=4)
