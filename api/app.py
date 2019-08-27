import os
import sys
import glob
import csv
import json
import traceback

from flask import Flask, jsonify, request

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from historic_hebrew_dates import create_parsers

app = Flask(__name__)


def pattern_path(lang, type):
    path = os.path.join('historic_hebrew_dates', 'patterns', f'{lang}_{type}.csv')
    if not os.path.exists(path):
        with open(path, "w+") as f:
            f.write("type,pattern,value\n")
    return path


@app.route("/api/patterns", methods=['GET'])
def overview():
    languages = {}
    for lang in glob.glob(os.path.join('historic_hebrew_dates', 'patterns', f'*.json')):
        key = os.path.splitext(os.path.basename(lang))[0]
        with open(lang) as description:
            languages[key] = json.load(description)
    return jsonify(languages)


@app.route("/api/patterns/<lang>/<type>", methods=['GET'])
def get(lang, type):
    with open(pattern_path(lang, type), encoding='utf-8-sig') as patterns:
        reader = csv.reader(patterns)
        return jsonify(list(reader))


@app.route("/api/patterns/<lang>/<type>", methods=['PUT'])
def put(lang, type):
    data = request.get_json()
    rows = data['rows']

    with open(pattern_path(lang, type), mode='w', encoding='utf-8-sig') as patterns:
        for row in rows:
            patterns.write(
                ','.join(map(lambda cell: f'"{cell}"' if ',' in cell else cell, row)) + '\n')

    return jsonify({'success': True})


@app.route("/api/parse/<lang>/<type>", methods=['POST'])
def parse(lang, type):
    data = request.get_json()
    input = data['input']
    rows = data['rows']
    parser = create_parsers(lang, override_rows={
        type: rows
    })[type]
    failure = False
    try:
        expression = parser.parse(input)
    except Exception as error:
        expression = str(error)
        failure = True
    else:
        if expression == None:
            evaluated = None
            failure = True
        else:
            try:
                evaluated = str(parser.parse(input, True))
            except Exception as error:
                evaluated = str(error)
                failure = True

    return jsonify({'expression': expression, 'evaluated': evaluated, 'error': failure})


@app.route("/api/search/<lang>/<type>", methods=['POST'])
def search(lang, type):
    data = request.get_json()
    input = data['input']
    rows = data['rows']
    parser = create_parsers(lang, override_rows={
        type: rows
    })[type]
    failure = False
    try:
        result = [escape_search(item) for item in list(parser.search(input))]
    except Exception as error:
        result = str(error)
        print(traceback.format_exc())
        failure = True

    return jsonify({'result': result, 'error': failure})


def escape_search(item):
    if 'eval' in item:
        item['eval'] = str(item['eval'])
    return item
