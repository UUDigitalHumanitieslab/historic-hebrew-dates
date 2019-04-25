#!/usr/bin/env python3
import sys
from .numeral_parser import NumeralParser
from .annotation_parser import AnnotatedCorpus


def main(args=None):
    """
    Main entry point.
    """
    if args is None:
        args = sys.argv[1:]

    text = ' '.join(args)
    parser = NumeralParser()
    expression = parser.parse_numeral(text)
    print(expression)
    evaluated = parser.evaluate_expression(expression)
    print(evaluated)

    c = AnnotatedCorpus(
        '/Users/3248526/git/historic-hebrew-dates/golden-standard/Inscription DB for Time Project.xlsx')
    print(c.as_infixed()['Transcription'].head())


if __name__ == "__main__":
    main()
