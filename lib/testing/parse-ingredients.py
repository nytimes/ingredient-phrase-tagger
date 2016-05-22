#!/usr/bin/env python
import sys
import os
import tempfile

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from training import utils


if len(sys.argv) < 2:
    sys.stderr.write('Usage: parse-ingredients.py FILENAME')
    sys.exit(1)

FILENAME = str(sys.argv[1])
_, tmpFile = tempfile.mkstemp()

with open(FILENAME) as infile, open(tmpFile, 'w') as outfile:
    outfile.write(utils.export_data(infile.readlines()))

tmpFilePath = "../../tmp/model_file"
modelFilename = os.path.join(os.path.dirname(__file__), tmpFilePath)
print "crf_test -v 1 -m %s %s" % (modelFilename, tmpFile)
os.system("crf_test -v 1 -m %s %s" % (modelFilename, tmpFile))
os.system("rm %s" % tmpFile)
