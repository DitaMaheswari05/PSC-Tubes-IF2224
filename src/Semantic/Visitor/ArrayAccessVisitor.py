# ini template aja, atur-atur sesuai kebutuhan

from typing import List
from Parser.ast import *
from src.Semantic.Visitor.SemanticAnalyzerBase import SemanticAnalyzerBase
from src.Semantic.Visitor.SemanticError import *
from src.Semantic.SymbolTable.SymbolTable import ObjectType, DataType
from src.Semantic.DecoratedAST.DecoratedASTNode import *
from Repository.TokenType import TokenType
from Model.Token import Token

class ArrayAccessVisitor(SemanticAnalyzerBase):
    # Visitor untuk semantic analysis array dan record access
    
    def _parse_identifier_factor(self, node: FactorNode) -> DecoratedASTNode:
        # Parse identifier yang bisa jadi variable, array access, atau record access
        return None
    
    def _parse_lvalue(self, children: List) -> DecoratedASTNode:
        # Parse left-hand side of assignment (variable, array access, record access)
        return None
    

    def visit_array_access(self, node: ArrayAccessASTNode) -> ArrayAccessASTNode:
        # Visit array access: arr[index]
        return None

    def visit_record_access(self, node: RecordAccessASTNode) -> RecordAccessASTNode:
        # Visit record access: rec.field
        return None

    def _validate_array_index(self, array_type: DataType, array_ref: int, index_node: DecoratedASTNode):
        # Validasi tipe index array (harus integer)
        return None

    def _validate_record_field(self, record_type: DataType, record_ref: int, field_name: str) -> int:
        # Validasi field ada dalam record, return tab_index field
        return None

    def _get_array_element_type(self, array_ref: int) -> tuple:
        # Get element type dari array (dari atab)
        return None

    def _get_record_field_info(self, record_ref: int, field_name: str) -> tuple:
        # Get field info dari record (dari btab)
        return None