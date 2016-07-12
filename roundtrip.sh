#!/bin/sh
COUNT_TRAIN=20000
COUNT_TEST=2000

echo "generating training data..."
bin/generate_data --data-path=nyt-ingredients-snapshot-2015.csv --count=$COUNT_TRAIN --offset=0 > tmp/train_file || exit 1

echo "generating test data..."
bin/generate_data --data-path=nyt-ingredients-snapshot-2015.csv --count=$COUNT_TEST --offset=$COUNT_TRAIN > tmp/test_file || exit 1

echo "training..."
crf_learn template_file tmp/train_file tmp/model_file || exit 1

echo "testing..."
crf_test -m tmp/model_file tmp/test_file > tmp/test_output || exit 1

echo "visualizing..."
ruby visualize.rb tmp/test_output > tmp/output.html || exit 1

echo "evaluating..."
FN=log/`date +%s`.txt
python bin/evaluate.py tmp/test_output > $FN || exit 1
cat $FN
