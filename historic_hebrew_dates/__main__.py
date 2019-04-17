#!/usr/bin/env python3
import sys
from .numeral_parser import NumeralParser

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

if __name__ == "__main__":
    main()
