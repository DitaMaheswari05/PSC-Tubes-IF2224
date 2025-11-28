from typing import List
from Parser.ast import *
from Semantic.Visitor.SemanticAnalyzerBase import SemanticAnalyzerBase
from Semantic.Visitor.SemanticError import *
from Semantic.SymbolTable.SymbolTable import *
from Semantic.DecoratedAST.DecoratedASTNode import *
from Semantic.Visitor.StatementVisitor import StatementVisitor
from Repository.TokenType import TokenType
from Model.Token import Token

class DeclarationVisitor(SemanticAnalyzerBase):
    # Visitor untuk semantic analysis declaration nodes
    
    def visit_declaration_part(self, node: DeclarationPartNode) -> List[DecoratedASTNode]:
        """Visit declaration part"""
        return None
    
    def visit_const_declaration(self, node: ConstDeclarationNode) -> List[ConstDeclASTNode]:
        """Visit constant declaration"""
        return None
    
    def visit_type_declaration(self, node: TypeDeclarationNode) -> List[TypeDeclASTNode]:
        """Visit type declaration"""
        return None
    
    def visit_var_declaration(self, node: VarDeclarationNode) -> List[VarDeclASTNode]:
        """Visit variable declaration"""
        return None
    
    def visit_procedure_declaration(self, node: ProcedureDeclarationNode) -> ProcedureDeclASTNode:
        """Visit procedure declaration (ada hubungan sama statement visitor)"""
        # Ambil nama prosedur
        return None
    
    def visit_function_declaration(self, node: FunctionDeclarationNode) -> FunctionDeclASTNode:
        """Visit function declaration (ada kaitan sama statement visitor)"""
        # Ambil nama fungsi dan return type
        return None
    
    def visit_formal_parameter_list(self, node: FormalParameterListNode) -> List[VarDeclASTNode]:
        """Visit formal parameter list"""
        return None