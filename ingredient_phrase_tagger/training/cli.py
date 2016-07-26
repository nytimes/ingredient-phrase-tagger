from __future__ import print_function

import re
import decimal
import argparse
import pandas as pd
from multiprocessing import Pool, TimeoutError, Queue, Process, Manager
from Queue import Empty

import utils


class Cli(object):
    def __init__(self, argv):
        self.opts = self._parse_args(argv)
        self._upstream_cursor = None
        m = Manager()
        self.output_queue = m.Queue()

    def run(self):
        self.generate_data(self.opts.count, self.opts.offset, self.opts.threads)

    def generate_data(self, count, offset, threads):
        """
        Generates training data in the CRF++ format for the ingredient
        tagging task
        """
        df = pd.read_csv(self.opts.data_path)
        df = df.fillna("")

        start = offset
        end = offset + count

        df_slice = df.iloc[start: end]

        qr = Process(target=self.start_queue_reader)
        qr.start()
        worker_pool = Pool(processes=threads or None)
        worker_pool.map_async(self._generate_data_worker, df_slice.iterrows())
        worker_pool.close()
        worker_pool.join()
        self.output_queue.put('DONE')
        qr.join()

    def _generate_data_worker(self, args):
            index, row = args
            out = []
            try:
                # extract the display name
                display_input = utils.cleanUnicodeFractions(row["input"])
                tokens = utils.tokenize(display_input)
                del(row["input"])

                rowData = self.addPrefixes([(t, self.matchUp(t, row)) for t in tokens])

                for i, (token, tags) in enumerate(rowData):
                    features = utils.getFeatures(token, i+1, tokens)
                    out.append(utils.joinLine([token] + features + [self.bestTag(tags)]))

            # ToDo: deal with this
            except UnicodeDecodeError:
                pass

            if out:
                self.output_queue.put('\n'.join(out))

    def start_queue_reader(self):
        o = None
        while o != 'DONE':
            try:
                o = self.output_queue.get()
                if o != 'DONE':
                    print(o, end="\n\n", flush=True)
            except Empty:
                pass

    def parseNumbers(self, s):
        """
        Parses a string that represents a number into a decimal data type so that
        we can match the quantity field in the db with the quantity that appears
        in the display name. Rounds the result to 2 places.
        """
        ss = utils.unclump(s)

        m3 = re.match('^\d+$', ss)
        if m3 is not None:
            return decimal.Decimal(round(float(ss), 2))

        m1 = re.match(r'(\d+)\s+(\d)/(\d)', ss)
        if m1 is not None:
            num = int(m1.group(1)) + (float(m1.group(2)) / float(m1.group(3)))
            return decimal.Decimal(str(round(num,2)))

        m2 = re.match(r'^(\d)/(\d)$', ss)
        if m2 is not None:
            num = float(m2.group(1)) / float(m2.group(2))
            return decimal.Decimal(str(round(num,2)))

        return None


    def matchUp(self, token, ingredientRow):
        """
        Returns our best guess of the match between the tags and the
        words from the display text.

        This problem is difficult for the following reasons:
            * not all the words in the display name have associated tags
            * the quantity field is stored as a number, but it appears
              as a string in the display name
            * the comment is often a compilation of different comments in
              the display name

        """
        ret = []

        # strip parens from the token, since they often appear in the
        # display_name, but are removed from the comment.
        token = utils.normalizeToken(token)
        decimalToken = self.parseNumbers(token)

        for key, val in ingredientRow.iteritems():
            if isinstance(val, basestring):

                for n, vt in enumerate(utils.tokenize(val)):
                    if utils.normalizeToken(vt) == token:
                        ret.append(key.upper())

            elif decimalToken is not None:
                try:
                    if val == decimalToken:
                        ret.append(key.upper())
                except:
                    pass

        return ret


    def addPrefixes(self, data):
        """
        We use BIO tagging/chunking to differentiate between tags
        at the start of a tag sequence and those in the middle. This
        is a common technique in entity recognition.

        Reference: http://www.kdd.cis.ksu.edu/Courses/Spring-2013/CIS798/Handouts/04-ramshaw95text.pdf
        """
        prevTags = None
        newData = []

        for n, (token, tags) in enumerate(data):

            newTags = []

            for t in tags:
                p = "B" if ((prevTags is None) or (t not in prevTags)) else "I"
                newTags.append("%s-%s" % (p, t))

            newData.append((token, newTags))
            prevTags = tags

        return newData


    def bestTag(self, tags):

        if len(tags) == 1:
            return tags[0]

        # if there are multiple tags, pick the first which isn't COMMENT
        else:
            for t in tags:
                if (t != "B-COMMENT") and (t != "I-COMMENT"):
                    return t

        # we have no idea what to guess
        return "OTHER"

    def _parse_args(self, argv):
        """
        Parse the command-line arguments into a dict.
        """

        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        parser.add_argument("--count", default=100, type=int, help=' ')
        parser.add_argument("--offset", default=0, type=int, help=' ')
        parser.add_argument("--threads", default=0, type=int, help=' ')
        parser.add_argument("--data-path", default="nyt-ingredients-snapshot-2015.csv", help=' ')

        return parser.parse_args(argv)
