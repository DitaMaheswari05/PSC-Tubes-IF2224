from typing import List, Optional
from Model.Token import Token
from Repository.TokenType import TokenType
from Parser.ast import *
from Parser.ErrorHandling import *
from Parser.declaration import DeclarationParser
from Parser.expression import ExpressionParser
from Parser.statements import StatementParser

class Parser:
    """
    Main Parser class untuk Pascal-S menggunakan Recursive Descent
    """
