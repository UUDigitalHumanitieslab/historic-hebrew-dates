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
            evaluated = parser.evaluate_expression(expression)
            print(evaluated)

def initial_patterns():
    c = AnnotatedCorpus()
    for p in c.parsed.loc[: , 'T_date']:
        if p != None:
            print(re.sub(r"(\{[^\}\(]*|\})", "", p).replace('(', '{').replace(')', '}'))


if __name__ == "__main__":
    main()
