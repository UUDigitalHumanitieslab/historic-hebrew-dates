import os
import sys
import csv
from flask import Flask, jsonify, request

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from historic_hebrew_dates import DateParser, DateTypeParser, MonthParser, NumeralParser

app = Flask(__name__)

type_parsers = {
    'dates': DateParser,
    'date_types': DateTypeParser,
    'months': MonthParser,
    'numerals': NumeralParser
}


def pattern_path(lang, type):
    return os.path.join('historic_hebrew_dates', 'patterns', f'{lang}_{type}.csv')


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
    parser = type_parsers[type](lang=lang, rows=rows)
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
                evaluated = str(parser.eval(expression))
            except Exception as error:
                evaluated = str(error)
                failure = True

    return jsonify({'expression': expression, 'evaluated': evaluated, 'error': failure})
