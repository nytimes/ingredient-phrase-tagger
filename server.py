from __future__ import print_function

from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from jsonrpc import JSONRPCResponseManager, dispatcher

import sys
import os
import tempfile
import json
import subprocess
import pdb

from ingredient_phrase_tagger.training import utils

def parse_ingredients(ingredients):
    # take out any characters not suited for json
    formatted_ingredients = [
        i.replace(u'\xa0', ' ') \
        .encode('ascii', 'ignore') \
        .encode('utf-8') \
    for i in ingredients ]
    _, tmpFile = tempfile.mkstemp()

    with open(tmpFile, 'w') as outfile:
        outfile.write(utils.export_data(formatted_ingredients))

    tmpFilePath = "tmp/model_file"
    modelFilename = os.path.join(os.path.dirname(__file__), tmpFilePath)
    command = ("crf_test -v 1 -m %s %s" % (modelFilename, tmpFile)).split(" ")

    proc = subprocess.Popen(command, stdout=subprocess.PIPE)
    output = proc.stdout.read()
    parsed_ingredients = utils.import_data(output.split('\n'))
    os.system("rm %s" % tmpFile)
    return [i for i in parsed_ingredients if i.get('name')]

@dispatcher.add_method
def parse_all(*args):
    return [parse_ingredients(i) for i in args]


@Request.application
def application(request):
    # Dispatcher is dictionary {<method_name>: callable}

    response = JSONRPCResponseManager.handle(
        request.data, dispatcher)
    return Response(response.json, mimetype='application/json')


if __name__ == '__main__':
    run_simple('localhost', 4000, application)