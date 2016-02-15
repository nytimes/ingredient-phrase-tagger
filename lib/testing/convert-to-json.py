#!/usr/bin/env python

"""
This thing takes the output of CRF++ and turns it into an actual
data structure.
"""

import sys
import os
import re
import string
import json

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from training import utils


if len(sys.argv) < 2:
    sys.stderr.write('Usage: make-data.py FILENAME')
    sys.exit(1)

data = [{}]
display = [[]]
prevTag = None

#
# iterate lines in the data file, which looks like:
#
#   # 0.511035
#   1/2       I1  L12  NoCAP  X  B-QTY/0.982850
#   teaspoon  I2  L12  NoCAP  X  B-UNIT/0.982200
#   fresh     I3  L12  NoCAP  X  B-COMMENT/0.716364
#   thyme     I4  L12  NoCAP  X  B-NAME/0.816803
#   leaves    I5  L12  NoCAP  X  I-NAME/0.960524
#   ,         I6  L12  NoCAP  X  B-COMMENT/0.772231
#   finely    I7  L12  NoCAP  X  I-COMMENT/0.825956
#   chopped   I8  L12  NoCAP  X  I-COMMENT/0.893379
#
#   # 0.505999
#   Black   I1  L8  YesCAP  X  B-NAME/0.765461
#   pepper  I2  L8  NoCAP   X  I-NAME/0.756614
#   ,       I3  L8  NoCAP   X  OTHER/0.798040
#   to      I4  L8  NoCAP   X  B-COMMENT/0.683089
#   taste   I5  L8  NoCAP   X  I-COMMENT/0.848617
#
# i.e. the output of crf_test -v 1
#
fn = str(sys.argv[1])
with open(fn) as file:
    for line in file:

        # ignore comments
        if line[0] == "#":
            pass

        # blank line starts a new ingredient
        elif line == "\n":
            data.append({})
            display.append([])
            prevTag = None

        # otherwise it's a token
        # e.g.: potato \t I2 \t L5 \t NoCAP \t B-NAME/0.978253
        else:

            columns = re.split(r'\t', string.strip(line))
            token = string.strip(columns[0])

            # unclump fractions
            token = utils.unclump(token)

            # turn B-NAME/123 back into "name"
            tag, confidence = re.split(r'/', columns[-1], 1)
            tag = re.sub(r'^[BI]\-', "", tag).lower()

            # ---- DISPLAY ----
            # build a structure which groups each token by its tag, so we can
            # rebuild the original display name later.

            if prevTag != tag:
                display[-1].append((tag, [token]))
                prevTag = tag

            else:
                display[-1][-1][1].append(token)
                #               ^- token
                #            ^---- tag
                #        ^-------- ingredient

            # ---- DATA ----
            # build a dict grouping tokens by their tag

            # initialize this attribute if this is the first token of its kind
            if tag not in data[-1]:
                data[-1][tag] = []

            # HACK: If this token is a unit, singularize it so Scoop accepts it.
            if tag == "unit":
                token = utils.singularize(token)

            data[-1][tag].append(token)

# reassemble the output into a list of dicts.

output = [
    dict([(k, utils.smartJoin(tokens)) for k, tokens in ingredient.iteritems()])
    for ingredient in data
    if len(ingredient)
]

# Add the marked-up display data
for i, v in enumerate(output):
    output[i]["display"] = utils.displayIngredient(display[i])

# Add the raw ingredient phrase
for i, v in enumerate(output):
    output[i]["input"] = utils.smartJoin(
        [" ".join(tokens) for k, tokens in display[i]])


print json.dumps(output, indent=4)
