# main nya
# ini template aja, atur-atur sesuai kebutuhan

from typing import List
from Parser.ast import *
from src.Semantic.Visitor.SemanticAnalyzerBase import SemanticAnalyzerBase
from src.Semantic.Visitor.SemanticError import *
from src.Semantic.SymbolTable.SymbolTable import *
from src.Semantic.DecoratedAST.DecoratedASTNode import *
from src.Semantic.Visitor.StatementVisitor import StatementVisitor
from src.Semantic.Visitor.DeclarationVisitor import DeclarationVisitor
from src.Semantic.Visitor.ExpressionVisitor import ExpressionVisitor
from src.Semantic.Visitor.ArrayAccessVisitor import ArrayAccessVisitor
from src.Semantic.Visitor.ProcFuncVisitor import ProcFuncVisitor
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