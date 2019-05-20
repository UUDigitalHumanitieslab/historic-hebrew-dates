
# parsetab.py
# This file is automatically generated. Do not edit.
# pylint: disable=W,C,R
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = 'LBRACE LPAREN RBRACE RPAREN WORDexpression : words\n                  | annotation\n                  | words annotation\n                  | words annotation expression\n                  | annotation expressionannotation : LBRACE expression RBRACE LPAREN WORD RPARENwords : WORD\n             | WORD words'
    
_lr_action_items = {'WORD':([0,3,4,5,6,12,14,],[4,4,4,4,4,13,-6,]),'LBRACE':([0,2,3,4,5,6,8,14,],[5,5,5,-7,5,5,-8,-6,]),'$end':([1,2,3,4,6,7,8,10,14,],[0,-1,-2,-7,-3,-5,-8,-4,-6,]),'RBRACE':([2,3,4,6,7,8,9,10,14,],[-1,-2,-7,-3,-5,-8,11,-4,-6,]),'LPAREN':([11,],[12,]),'RPAREN':([13,],[14,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'expression':([0,3,5,6,],[1,7,9,10,]),'words':([0,3,4,5,6,],[2,2,8,2,2,]),'annotation':([0,2,3,5,6,],[3,6,3,3,3,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> expression","S'",1,None,None,None),
  ('expression -> words','expression',1,'p_expression','annotation_parser.py',28),
  ('expression -> annotation','expression',1,'p_expression','annotation_parser.py',29),
  ('expression -> words annotation','expression',2,'p_expression','annotation_parser.py',30),
  ('expression -> words annotation expression','expression',3,'p_expression','annotation_parser.py',31),
  ('expression -> annotation expression','expression',2,'p_expression','annotation_parser.py',32),
  ('annotation -> LBRACE expression RBRACE LPAREN WORD RPAREN','annotation',6,'p_annotation','annotation_parser.py',36),
  ('words -> WORD','words',1,'p_words','annotation_parser.py',43),
  ('words -> WORD words','words',2,'p_words','annotation_parser.py',44),
]
