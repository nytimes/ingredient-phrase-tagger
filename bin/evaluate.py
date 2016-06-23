#!/usr/bin/env python
import sys


if len(sys.argv) < 2:
    sys.stderr.write('Usage: evaluate.py FILENAME')
    sys.exit(1)

filename = sys.argv[1]

# load CRF++ output for test data
with open(filename, 'r') as file:
    sentences = file.read().split('\n\n')

total_sentences = len(sentences)
total_words, correct_words, correct_sentences = 0, 0, 0

# loop over each sentence
for sentence in sentences:
    correct_words_per_sentence = 0
    total_words_per_sentence = 0

    # loop over each word in the sentence
    # data for each word is on a separate line
    for word in sentence.split('\n'):
        line = word.strip().split('\t')

        if len(line) > 1:
            word = line[0]
            guess = line[-2]
            gold = line[-1]

            # we do not count commas
            if word.strip() not in [',']:

                #increment global word count
                total_words += 1
                total_words_per_sentence += 1

                if (guess == gold) or (guess[2:] == gold[2:]):
                    correct_words +=1
                    correct_words_per_sentence += 1

    if total_words_per_sentence == correct_words_per_sentence:
        correct_sentences += 1

print
print 'Sentence-Level Stats:'
print '\tcorrect: ', correct_sentences
print '\ttotal: ', total_sentences
print '\t% correct: ', 100 * (correct_sentences / float(total_sentences))

print
print 'Word-Level Stats:'
print '\tcorrect:', correct_words
print '\ttotal:', total_words
print '\t% correct:', 100 * (correct_words / float(total_words))
