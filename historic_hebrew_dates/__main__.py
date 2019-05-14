#!/usr/bin/env python3
import sys
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
        parser = NumeralParser()
        expression = parser.parse_numeral(text)
        print(expression)
        evaluated = parser.evaluate_expression(expression)
        print(evaluated)

    c = AnnotatedCorpus()
    # print(c.parsed.loc[0])  # print the first entry of the parsed dataframe


if __name__ == "__main__":
    main()
