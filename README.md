# CRF Ingredient Parser
This directory contains the scripts necessary to train and test a model for tagging
recipe ingredient parts using the tags QUANTITY, UNIT, NAME, COMMENT and OTHER.

The ingredient parser uses a conditional random field model (CRF) to predict the
ingredient tags from labeled training data. More information about CRFs can be
found [here](http://people.cs.umass.edu/~mccallum/papers/crf-tutorial.pdf). Training
the model takes roughly 30 minutes for 130k examples using the
[CRF++](https://taku910.github.io/crfpp/) library.

## Development
```
brew install crf++
pip install -r requirements.txt`
```

## Roundtrip
To run this model locally, you will first need to train the model. If you
train the model, you might as well test it to see if it is working as
expected.

To run the entire process (training + testing):

    ./roundtrip.sh

You can edit this script to specify the size of your training and testing
set. The default is 130k training examples and 30k test examples.

## Training
To train the model, run the following commands where count specifies the number of
training examples (i.e. ingredients) and offset specifies which training example to
start with. There are roughly 160k examples in the D.U.

`bin/generate_data --count=130000 --offset=0 > tmp/train_file`
`crf_learn template_file tmp/train_file tmp/model_file`

The output of generate_data something like:
    1       I1      L8      NoCAP   NoPAREN B-QTY
    cup     I2      L8      NoCAP   NoPAREN B-UNIT
    white   I3      L8      NoCAP   NoPAREN B-NAME
    wine    I4      L8      NoCAP   NoPAREN I-NAME

    1/2     I1      L4      NoCAP   NoPAREN B-QTY
    cup     I2      L4      NoCAP   NoPAREN B-UNIT
    sugar   I3      L4      NoCAP   NoPAREN B-NAME


    2       I1      L8      NoCAP   NoPAREN B-QTY
    tablespoons     I2      L8      NoCAP   NoPAREN B-UNIT
    dry     I3      L8      NoCAP   NoPAREN B-NAME
    white   I4      L8      NoCAP   NoPAREN I-NAME
    wine    I5      L8      NoCAP   NoPAREN I-NAME

## Testing
You need to run two python scripts to test. The first one, called
`parse-ingredients.py`, takes a line seperated list of ingredients and outputs the
results in the CRF++ format, shown above. The script convert-to-json, takes this
output and returns the results in a JSON format.

```./lib/testing/parse-ingredients.py ingredients.txt > results.txt```


```./lib/testing/convert-to-json.py results.txt > results.json```

The file `ingredients.txt` contains something like:

    1 pound carrots, young ones if possible
    Kosher salt, to taste
    2 tablespoons sherry vinegar
    2 tablespoons honey
    2 tablespoons extra-virgin olive oil
    1 medium-size shallot, peeled and finely diced
    1/2 teaspoon fresh thyme leaves, finely chopped
    Black pepper, to taste
