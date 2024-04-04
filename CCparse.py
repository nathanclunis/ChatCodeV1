import CClex
from CClex import lexer, tokens
from lark import Lark

with open('CCgrammar.lark', 'r') as grammar_file:
    grammar = grammar_file.read()

parser = Lark(grammar, start='program')

