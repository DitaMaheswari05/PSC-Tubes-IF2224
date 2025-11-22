# ini template aja, atur-atur sesuai kebutuhan

from typing import List
from Parser.ast import *
from Semantic.SemanticAnalyzerBase import SemanticAnalyzerBase
from Semantic.SemanticError import *
from Semantic.SymbolTable import *
from Semantic.DecoratedASTNode import *
from Repository.TokenType import TokenType
from Model.Token import Token

class ProcFuncVisitor(SemanticAnalyzerBase):
    # Visitor untuk semantic analysis procedure dan function call
    
    def visit_procedure_call(self, node: CallStatementNode) -> ProcCallASTNode:
        # Visit procedure call
        ast_node = None
        # <isi disini>
        return ast_node
    
    def visit_function_call(self, node: CallStatementNode) -> FuncCallASTNode:
        # Visit function call
        ast_node = None
        # <isi disini>
        return ast_node
    

    def _validate_call_arguments(self, name: str, tab_index: int, args: List[DecoratedASTNode]):
        """
        Validasi:
        - Jumlah argumen sesuai
        - Tipe argumen kompatibel dengan parameter
        - By-reference parameter (var) hanya menerima lvalue
        """
        return None

    def _get_parameter_list(self, tab_index: int) -> List[tuple]:
        """
        Get list parameter dari procedure/function
        Return: [(param_name, param_type, is_var_param), ...]
        """
        return None

    def _check_builtin_procedure(self, name: str, args: List[DecoratedASTNode]):
        """
        Validasi built-in procedures: writeln, write, readln, read
        - writeln/write: bisa variadic
        - readln/read: hanya variable (lvalue)
        """
        return None

    def _get_function_return_type(self, tab_index: int) -> DataType:
        """Get return type dari function"""
        return None