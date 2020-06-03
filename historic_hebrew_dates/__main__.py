#!/usr/bin/env python3
import sys
import re
from .annotated_corpus import AnnotatedCorpus
from .pattern_factory import create_parsers


def NumeralParser(): return create_parsers('hebrew')['numerals']


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
            result = parser.parse(text)
            for token_matches in result:
                for match in token_matches:
                    print(match.value)
                    print(match.evaluated)


def initial_patterns():
    c = AnnotatedCorpus()
    print(c.write_patterns())


if __name__ == "__main__":
    main()
