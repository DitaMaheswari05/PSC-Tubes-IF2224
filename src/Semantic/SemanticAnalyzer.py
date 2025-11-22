# main nya
# ini template aja, atur-atur sesuai kebutuhan

from typing import List
from Parser.ast import *
from Semantic.SemanticAnalyzerBase import SemanticAnalyzerBase
from Semantic.SemanticError import *
from Semantic.SymbolTable import *
from Semantic.DecoratedASTNode import *
from Semantic.StatementVisitor import StatementVisitor
from Semantic.DeclarationVisitor import DeclarationVisitor
from Semantic.ExpressionVisitor import ExpressionVisitor
from Semantic.ArrayAccessVisitor import ArrayAccessVisitor
from Semantic.ProcFuncVisitor import ProcFuncVisitor
from Repository.TokenType import TokenType
from Model.Token import Token

class SemanticAnalyzer(SemanticAnalyzerBase):
    def __init__(self):
        super().__init__()
        self.declaration_visitor = DeclarationVisitor()
        self.statement_visitor = StatementVisitor()
        self.expression_visitor = ExpressionVisitor()
        self.array_visitor = ArrayAccessVisitor()
        self.proc_func_visitor = ProcFuncVisitor()
        
        # Share symbol table across all visitors
        for visitor in [self.declaration_visitor, self.statement_visitor, 
                       self.expression_visitor, self.array_visitor, 
                       self.proc_func_visitor]:
            visitor.symbol_table = self.symbol_table
    
    def analyze(self, parse_tree: ProgramNode) -> ProgramASTNode:
        # Main entry point untuk semantic analysis
        return None
    
    def visit_program(self, node: ProgramNode) -> ProgramASTNode:
        # Visit program root
        return None