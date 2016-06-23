#!/usr/bin/env python
import re
import string


def tokenize(s):
    """
    Tokenize on parenthesis, punctuation, spaces and American units followed by a slash.

    We sometimes give American units and metric units for baking recipes. For example:
        * 2 tablespoons/30 mililiters milk or cream
        * 2 1/2 cups/300 grams all-purpose flour

    The recipe database only allows for one unit, and we want to use the American one.
    But we must split the text on "cups/" etc. in order to pick it up.
    """

    american_units = ['cup', 'tablespoon', 'teaspoon', 'pound', 'ounce', 'quart', 'pint']
    for unit in american_units:
        s = s.replace(unit + '/', unit + ' ')
        s = s.replace(unit + 's/', unit + 's ')

    return filter(None, re.split(r'([,\(\)])?\s*', clumpFractions(s)))

def joinLine(columns):
    return "\t".join(columns)

def clumpFractions(s):
    """
    Replaces the whitespace between the integer and fractional part of a quantity
    with a dollar sign, so it's interpreted as a single token. The rest of the
    string is left alone.

        clumpFractions("aaa 1 2/3 bbb")
        # => "aaa 1$2/3 bbb"
    """
    return re.sub(r'(\d+)\s+(\d)/(\d)', r'\1$\2/\3', s)

def cleanUnicodeFractions(s):
    """
    Replace unicode fractions with ascii representation, preceded by a
    space.

    "1\x215e" => "1 7/8"
    """

    fractions = {
        u'\x215b': '1/8',
        u'\x215c': '3/8',
        u'\x215d': '5/8',
        u'\x215e': '7/8',
        u'\x2159': '1/6',
        u'\x215a': '5/6',
        u'\x2155': '1/5',
        u'\x2156': '2/5',
        u'\x2157': '3/5',
        u'\x2158': '4/5',
        u'\xbc': ' 1/4',
        u'\xbe': '3/4',
        u'\x2153': '1/3',
        u'\x2154': '2/3',
        u'\xbd': '1/2',
    }

    for f_unicode, f_ascii in fractions.items():
        s = s.replace(f_unicode, ' ' + f_ascii)

    return s

def unclump(s):
    """
    Replacess $'s with spaces. The reverse of clumpFractions.
    """
    return re.sub(r'\$', " ", s)

def normalizeToken(s):
    """
    ToDo: FIX THIS. We used to use the pattern.en package to singularize words, but
    in the name of simple deployments, we took it out. We should fix this at some
    point.
    """
    return singularize(s)

def getFeatures(token, index, tokens):
    """
    Returns a list of features for a given token.
    """
    length = len(tokens)

    return [
        ("I%s" % index),
        ("L%s" % lengthGroup(length)),
        ("Yes" if isCapitalized(token) else "No") + "CAP",
        ("Yes" if insideParenthesis(token, tokens) else "No") + "PAREN"
    ]

def singularize(word):
    """
    A poor replacement for the pattern.en singularize function, but ok for now.
    """

    units = {
        "cups": u"cup",
        "tablespoons": u"tablespoon",
        "teaspoons": u"teaspoon",
        "pounds": u"pound",
        "ounces": u"ounce",
        "cloves": u"clove",
        "sprigs": u"sprig",
        "pinches": u"pinch",
        "bunches": u"bunch",
        "slices": u"slice",
        "grams": u"gram",
        "heads": u"head",
        "quarts": u"quart",
        "stalks": u"stalk",
        "pints": u"pint",
        "pieces": u"piece",
        "sticks": u"stick",
        "dashes": u"dash",
        "fillets": u"fillet",
        "cans": u"can",
        "ears": u"ear",
        "packages": u"package",
        "strips": u"strip",
        "bulbs": u"bulb",
        "bottles": u"bottle"
    }

    if word in units.keys():
        return units[word]
    else:
        return word

def isCapitalized(token):
    """
    Returns true if a given token starts with a capital letter.
    """
    return re.match(r'^[A-Z]', token) is not None

def lengthGroup(actualLength):
    """
    Buckets the length of the ingredient into 6 buckets.
    """
    for n in [4, 8, 12, 16, 20]:
        if actualLength < n:
            return str(n)

    return "X"

def insideParenthesis(token, tokens):
    """
    Returns true if the word is inside parenthesis in the phrase.
    """
    if token in ['(', ')']:
        return True
    else:
        line = " ".join(tokens)
        return re.match(r'.*\(.*'+re.escape(token)+'.*\).*',  line) is not None

def displayIngredient(ingredient):
    """
    Format a list of (tag, [tokens]) tuples as an HTML string for display.

        displayIngredient([("qty", ["1"]), ("name", ["cat", "pie"])])
        # => <span class='qty'>1</span> <span class='name'>cat pie</span>
    """

    return "".join([
        "<span class='%s'>%s</span>" % (tag, " ".join(tokens))
        for tag, tokens in ingredient
    ])

# HACK: fix this
def smartJoin(words):
    """
    Joins list of words with spaces, but is smart about not adding spaces
    before commas.
    """

    input = " ".join(words)

    # replace " , " with ", "
    input = input.replace(" , ", ", ")

    # replace " ( " with " ("
    input = input.replace("( ", "(")

    # replace " ) " with ") "
    input = input.replace(" )", ")")

    return input


def import_data(lines):
    """
    This thing takes the output of CRF++ and turns it into an actual
    data structure.
    """
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
    for line in lines:
        # blank line starts a new ingredient
        if line in ('', '\n'):
            data.append({})
            display.append([])
            prevTag = None

        # ignore comments
        elif line[0] == "#":
            pass

        # otherwise it's a token
        # e.g.: potato \t I2 \t L5 \t NoCAP \t B-NAME/0.978253
        else:

            columns = re.split('\t', line.strip())
            token = columns[0].strip()

            # unclump fractions
            token = unclump(token)

            # turn B-NAME/123 back into "name"
            tag, confidence = re.split(r'/', columns[-1], 1)
            tag = re.sub('^[BI]\-', "", tag).lower()

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
                token = singularize(token)

            data[-1][tag].append(token)

    # reassemble the output into a list of dicts.
    output = [
        dict([(k, smartJoin(tokens)) for k, tokens in ingredient.iteritems()])
        for ingredient in data
        if len(ingredient)
        ]
    # Add the marked-up display data
    for i, v in enumerate(output):
        output[i]["display"] = displayIngredient(display[i])

    # Add the raw ingredient phrase
    for i, v in enumerate(output):
        output[i]["input"] = smartJoin(
            [" ".join(tokens) for k, tokens in display[i]])

    return output


def export_data(lines):
    """ Parse "raw" ingredient lines into CRF-ready output """
    output = []
    for line in lines:
        line_clean = re.sub('<[^<]+?>', '', line)
        tokens = tokenize(line_clean)

        for i, token in enumerate(tokens):
            features = getFeatures(token, i+1, tokens)
            output.append(joinLine([token] + features))
        output.append('')
    return '\n'.join(output)
