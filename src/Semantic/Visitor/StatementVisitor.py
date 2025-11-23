# ini template aja, atur-atur sesuai kebutuhan

from typing import Optional, List
from Parser.ast import *
from src.Semantic.Visitor.SemanticAnalyzerBase import SemanticAnalyzerBase
from src.Semantic.Visitor.SemanticError import SemanticError, TypeMismatchError
from src.Semantic.SymbolTable.SymbolTable import ObjectType, DataType
from src.Semantic.DecoratedAST.DecoratedASTNode import *
from src.Semantic.Visitor.ExpressionVisitor import ExpressionVisitor
# kayaknya juga butuh array, proc and func visitor
from Repository.TokenType import TokenType
from Model.Token import Token

class StatementVisitor(SemanticAnalyzerBase):
    # Visitor untuk semantic analysis statement nodes
    
    def visit_compound_statement(self, node: CompoundStatementNode) -> BlockASTNode:
        # Visit compound statement
        return None
    
    def visit_statement_list(self, node: StatementListNode) -> List[DecoratedASTNode]:
        # Visit statement list
        return None
    
    def visit_statement(self, node) -> Optional[DecoratedASTNode]:
        
        return None
    
    def visit_assignment_statement(self, node: AssignmentStatementNode) -> AssignASTNode:
        # Visit assignment statement
        return None
    
    def visit_if_statement(self, node: IfStatementNode) -> IfASTNode:
        # Visit if statement
        return None
    
    def visit_while_statement(self, node: WhileStatementNode) -> WhileASTNode:
        # Visit while statement
        return None
    
    def visit_for_statement(self, node: ForStatementNode) -> ForASTNode:
        # Visit for statement
        return None
    
    def visit_repeat_statement(self, node: RepeatStatementNode) -> RepeatASTNode:
        # Visit repeat statement
        return None
    
    def visit_case_statement(self, node: CaseStatementNode) -> CaseASTNode:
        # Visit case statement
        return None