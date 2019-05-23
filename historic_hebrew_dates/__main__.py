#!/usr/bin/env python3
import sys
import re
from .annotated_corpus import AnnotatedCorpus
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
            expression = parser.parse(text)
            print(expression)
            evaluated = parser.eval(expression)
            print(evaluated)

def initial_patterns():
    c = AnnotatedCorpus()
    print(c.write_patterns())


if __name__ == "__main__":
    main()
