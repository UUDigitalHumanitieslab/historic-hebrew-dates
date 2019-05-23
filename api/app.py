import os
import csv
from flask import Flask, jsonify

app = Flask(__name__)

def pattern_path(lang, type):
    return os.path.join('historic_hebrew_dates', 'patterns', f'{lang}_{type}.csv')

@app.route("/api/patterns/<lang>/<type>", methods=['GET'])
def get(lang, type):
    with open(pattern_path(lang, type)) as patterns:
        reader = csv.reader(patterns)
        return jsonify(list(reader))
