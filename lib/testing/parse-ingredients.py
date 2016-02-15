#!/usr/bin/env python

import sys
import os
import re

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from training import utils

if len(sys.argv) < 2:
    sys.stderr.write('Usage: parse-ingredients.py FILENAME')
    sys.exit(1)

FILENAME = str(sys.argv[1])
tmpFile = FILENAME + ".tmp"

with open(FILENAME) as infile, open(tmpFile, 'w') as outfile:
    for line in infile:
        line_clean = re.sub('<[^<]+?>', '', line)
        tokens = utils.tokenize(line_clean)

        for i, token in enumerate(tokens):
            features = utils.getFeatures(token, i+1, tokens)
            outfile.write(utils.joinLine([token] + features) + "\n")
        outfile.write("\n")

tmpFilePath = "../../tmp/model_file"
modelFilename = os.path.join(os.path.dirname(__file__), tmpFilePath)
os.system("crf_test -v 1 -m %s %s" % (modelFilename, tmpFile))
os.system("rm %s" % tmpFile)
