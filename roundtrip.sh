#!/bin/sh
COUNT_TRAIN=150000
COUNT_TEST=15000

echo "generating training data..."
bin/generate_data --data-path=hacked_data.csv --count=$COUNT_TRAIN --offset=0 > tmp/train_file || exit 1

echo "generating test data..."
bin/generate_data --data-path=hacked_data.csv --count=$COUNT_TEST --offset=$COUNT_TRAIN > tmp/test_file || exit 1

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
