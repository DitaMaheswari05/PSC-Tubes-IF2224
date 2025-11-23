# ini template aja, atur-atur sesuai kebutuhan
from Parser.ast import *
from src.Semantic.Visitor.SemanticAnalyzerBase import SemanticAnalyzerBase
from src.Semantic.Visitor.SemanticError import *
from src.Semantic.SymbolTable.SymbolTable import *
from src.Semantic.DecoratedAST.DecoratedASTNode import *
from src.Semantic.Visitor.ArrayAccessVisitor import ArrayAccessVisitor
from src.Semantic.Visitor.ProcFuncVisitor import ProcFuncVisitor
from Repository.TokenType import TokenType
from Model.Token import Token

class ExpressionVisitor(SemanticAnalyzerBase):
    # Visitor untuk semantic analysis expression nodes
    
    def visit_expression(self, node: ExpressionNode) -> DecoratedASTNode:
        # Visit expression
        # expression -> simple-expression (relop simple-expression)?
        
        return None
    
    def visit_simple_expression(self, node: SimpleExpressionNode) -> DecoratedASTNode:
        # Visit simple expression
        # simple-expression -> (sign)? term (addop term)*
        
        return None
    
    def visit_term(self, node: TermNode) -> DecoratedASTNode:
        # Visit term
        # term -> factor (mulop factor)*
        return None
    
    def visit_factor(self, node: FactorNode) -> DecoratedASTNode:
        # Visit factor
        # factor -> NUMBER | STRING | CHAR | IDENTIFIER | function-call | 
        #           array-access | record-access | (expression) | NOT factor
        return None
    
    def visit_parameter_list(self, node: ParameterListNode) -> list:
        # Visit parameter list
        return None
    
    def _create_binary_op(self, op: str, left: DecoratedASTNode, right: DecoratedASTNode) -> BinOpASTNode:
        # Create binary operation node dengan type checking
        return None

    def _check_type_compatibility(self, left_type: DataType, right_type: DataType, op: str) -> DataType:
        # Cek kompatibilitas tipe untuk operasi dan return result type
        return None

    def _infer_expression_type(self, node: DecoratedASTNode) -> DataType:
        # Infer tipe dari expression node
        return None