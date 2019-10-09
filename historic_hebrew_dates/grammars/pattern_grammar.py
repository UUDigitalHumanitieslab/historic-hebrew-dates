import re
import uuid
from typing import Dict, List, Union, Pattern, Tuple

tokens = (
    'LBRACE',
    'RBRACE',
    'COLON',
    'NUMBER',
    'WORD'
)

t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_COLON = r':'
t_NUMBER = r'[0-9]+'
t_WORD = r'[^\{\}:0-9]+'

t_ignore = "\r\t"


def t_error(t):
    raise Exception("Illegal character '%s'" % t.value[0])


# Build the lexer
import ply.lex as lex
lexer = lex.lex(reflags=re.UNICODE)


def p_pattern(p):
    '''pattern : words
               | sub
               | words sub'''
    p[0] = p[1:]


def p_pattern_multiple(p):
    '''pattern : words sub pattern
               | sub pattern'''
    terms = len(p)
    p[0] = p[1:terms-1] + p[terms-1]


def p_sub(p):
    # Reference to a sub pattern, e.g. {name} or {name:type}
    # Where type refers to the name of the other pattern to use.
    # If no type is given the name is also used to identify the other pattern.
    # For example if a year pattern has only month sub-pattern it allows
    # writing this as {month} instead of {month:month}.
    '''sub : LBRACE WORD RBRACE
           | LBRACE NUMBER RBRACE
           | LBRACE WORD COLON WORD RBRACE
           | LBRACE WORD COLON NUMBER RBRACE'''
    typed = len(p) == 6

    type = p[4] if typed else p[2]
    p[0] = {
        'name': p[2],
        'type': 'backref' if re.match('^\d+$', type) else type
    }


def p_sub_numbered(p):
    '''sub : LBRACE WORD NUMBER COLON WORD RBRACE'''
    mapped = p[0:2] + [p[2] + p[3]] + p[4:]
    p_sub(mapped)
    p[0] = mapped[0]


def p_sub_numbered_untyped(p):
    '''sub : LBRACE WORD NUMBER RBRACE'''
    mapped = p[0:2] + [p[2] + p[3]] + [':', p[2], p[4]]
    p_sub(mapped)
    p[0] = mapped[0]


def p_words(p):
    '''words : WORD
             | NUMBER
             | NUMBER words
             | WORD words'''
    if len(p) == 2:
        p[0] = {'words': [p[1]]}
    else:
        p[0] = {'words': [p[1]] + p[2]['words']}


def p_error(p):
    raise Exception("Syntax error at '%s (%s, %s)'" %
                    (p.value, p.lexpos, p.type))


import ply.yacc as yacc
parser = yacc.yacc(tabmodule='pattern_parsetab', debugfile='pattern.out')


def get_parts(pattern: str) -> List[Dict[str, str]]:
    try:
        return parser.parse(pattern, lexer=lexer)
    except Exception as error:
        raise Exception("Could not parse %s" % pattern)


if __name__ == "__main__":
    # interactive mode for testing from console
    type_patterns = {}
    preceding_patterns = []
    while True:
        try:
            s = input('input > ')
            if not s:
                quit()
        except EOFError:
            break
        try:
            [name, pattern] = s.split('=', 1)
            name = name.rstrip()
            pattern = pattern.lstrip()
        except ValueError:
            name = None
            pattern = s
        parts = parser.parse(pattern)
        print(parts)
