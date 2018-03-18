#!/usr/bin/env python
from __future__ import print_function
import fileinput

import json

from ingredient_phrase_tagger.training import utils

print(json.dumps(utils.import_data(fileinput.input()), indent=4))
fileinput.close()
