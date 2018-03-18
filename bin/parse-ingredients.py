#!/usr/bin/env python
from __future__ import print_function

import sys
import os
import tempfile
import fileinput
import pdb

from ingredient_phrase_tagger.training import utils

_, tmpFile = tempfile.mkstemp()

with open(tmpFile, 'w') as outfile:
    outfile.write(utils.export_data(fileinput.input()))

tmpFilePath = "../tmp/model_file"
modelFilename = os.path.join(os.path.dirname(__file__), tmpFilePath)
os.system("crf_test -v 1 -m %s %s" % (modelFilename, tmpFile))
os.system("rm %s" % tmpFile)

fileinput.close()
