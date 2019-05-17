#!/usr/bin/env python3
import sys
import re
from .annotation_parser import AnnotatedCorpus
from .numeral_parser import NumeralParser


def main(args=None):
    """
    Main entry point.
    """
    if args is None:
        args = sys.argv[1:]

    text = ' '.join(args)
    if text:
        if text == 'initial_patterns':
            initial_patterns()
        else:
            parser = NumeralParser()
            expression = parser.parse_numeral(text)
            print(expression)
            evaluated = parser.eval(expression)
            print(evaluated)

def initial_patterns():
    c = AnnotatedCorpus()
    for p in zip(c.parsed.loc[:, 'Type'], c.parsed.loc[:, 'T_date_type']):
        if p[0] != None and p[1] != None:
            print(f'{p[0]},{p[1]}')


if __name__ == "__main__":
    main()
