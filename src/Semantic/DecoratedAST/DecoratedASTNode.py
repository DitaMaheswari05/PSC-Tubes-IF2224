from typing import List, Optional, Any
from Parser.ast import ASTNode
from src.Semantic.SymbolTable.SymbolTable import *

class DecoratedASTNode(ASTNode):
    def __init__(self, node_type: str):
        super().__init__(node_type)
        self.data_type: Optional[DataType] = None # tipe data hasil evaluasi
        self.tab_index: Optional[int] = None # indeks ke symbol table
        self.block_index: Optional[int] = None # indeks ke block table
        self.scope_level: Optional[int] = None # level scope
    
    def annotate(self, data_type: DataType = None, tab_index: int = None, 
                 block_index: int = None, scope_level: int = None):
        # Menambahkan anotasi ke node
        if data_type is not None:
            self.data_type = data_type
        if tab_index is not None:
            self.tab_index = tab_index
        if block_index is not None:
            self.block_index = block_index
        if scope_level is not None:
            self.scope_level = scope_level
    
    def to_string(self, indent: int = 0) -> str:
        # Override untuk menampilkan anotasi
        prefix = "│   " * indent
        if indent > 0:
            prefix = "│   " * (indent - 1) + "├── "
        
        # Tambahkan informasi anotasi
        annotations = []
        if self.data_type is not None:
            annotations.append(f"type:{self.data_type.name.lower()}")
        if self.tab_index is not None:
            annotations.append(f"tab:{self.tab_index}")
        if self.scope_level is not None:
            annotations.append(f"lev:{self.scope_level}")
        
        annotation_str = f" [{', '.join(annotations)}]" if annotations else ""
        result = f"{prefix}<{self.node_type}>{annotation_str}\n"
        
        for i, child in enumerate(self.children):
            is_last = (i == len(self.children) - 1)
            
            if isinstance(child, ASTNode):
                result += child.to_string(indent + 1)
            else:
                # Token atau nilai lainnya
                child_prefix = "│   " * indent + "├── "
                if is_last:
                    child_prefix = "│   " * indent + "└── "
                result += f"{child_prefix}{str(child)}\n"
        
        return result

# Decorated node classes untuk AST yang lebih sederhana
class ProgramASTNode(DecoratedASTNode):
    def __init__(self, name: str):
        super().__init__("Program")
        self.name = name
        self.declarations: List[DecoratedASTNode] = []
        self.block: Optional[DecoratedASTNode] = None

class VarDeclASTNode(DecoratedASTNode):
    def __init__(self, name: str, var_type: DataType):
        super().__init__("VarDecl")
        self.name = name
        self.var_type = var_type

class ConstDeclASTNode(DecoratedASTNode):
    def __init__(self, name: str, value: Any, const_type: DataType):
        super().__init__("ConstDecl")
        self.name = name
        self.value = value
        self.const_type = const_type

class TypeDeclASTNode(DecoratedASTNode):
    def __init__(self, name: str, type_def: DataType):
        super().__init__("TypeDecl")
        self.name = name
        self.type_def = type_def

class ProcedureDeclASTNode(DecoratedASTNode):
    def __init__(self, name: str):
        super().__init__("ProcedureDecl")
        self.name = name
        self.parameters: List[DecoratedASTNode] = []
        self.declarations: List[DecoratedASTNode] = []
        self.block: Optional[DecoratedASTNode] = None

class FunctionDeclASTNode(DecoratedASTNode):
    def __init__(self, name: str, return_type: DataType):
        super().__init__("FunctionDecl")
        self.name = name
        self.return_type = return_type
        self.parameters: List[DecoratedASTNode] = []
        self.declarations: List[DecoratedASTNode] = []
        self.block: Optional[DecoratedASTNode] = None

class BlockASTNode(DecoratedASTNode):
    def __init__(self):
        super().__init__("Block")
        self.statements: List[DecoratedASTNode] = []

class AssignASTNode(DecoratedASTNode):
    def __init__(self, target: DecoratedASTNode, value: DecoratedASTNode):
        super().__init__("Assign")
        self.target = target
        self.value = value

class VarASTNode(DecoratedASTNode):
    def __init__(self, name: str):
        super().__init__("Var")
        self.name = name

class NumberASTNode(DecoratedASTNode):
    def __init__(self, value: Any):
        super().__init__("Number")
        self.value = value
        # Tentukan tipe berdasarkan nilai
        if isinstance(value, int):
            self.data_type = DataType.INTEGER
        elif isinstance(value, float):
            self.data_type = DataType.REAL

class StringASTNode(DecoratedASTNode):
    def __init__(self, value: str):
        super().__init__("String")
        self.value = value
        self.data_type = DataType.STRING

class CharASTNode(DecoratedASTNode):
    def __init__(self, value: str):
        super().__init__("Char")
        self.value = value
        self.data_type = DataType.CHAR

class BooleanASTNode(DecoratedASTNode):
    def __init__(self, value: bool):
        super().__init__("Boolean")
        self.value = value
        self.data_type = DataType.BOOLEAN

class BinOpASTNode(DecoratedASTNode):
    def __init__(self, op: str, left: DecoratedASTNode, right: DecoratedASTNode):
        super().__init__("BinOp")
        self.op = op
        self.left = left
        self.right = right

class UnaryOpASTNode(DecoratedASTNode):
    def __init__(self, op: str, operand: DecoratedASTNode):
        super().__init__("UnaryOp")
        self.op = op
        self.operand = operand

class ProcCallASTNode(DecoratedASTNode):
    def __init__(self, name: str, args: List[DecoratedASTNode]):
        super().__init__("ProcCall")
        self.name = name
        self.args = args

class FuncCallASTNode(DecoratedASTNode):
    def __init__(self, name: str, args: List[DecoratedASTNode]):
        super().__init__("FuncCall")
        self.name = name
        self.args = args

class IfASTNode(DecoratedASTNode):
    def __init__(self, condition: DecoratedASTNode, then_stmt: DecoratedASTNode, 
                 else_stmt: Optional[DecoratedASTNode] = None):
        super().__init__("If")
        self.condition = condition
        self.then_stmt = then_stmt
        self.else_stmt = else_stmt

class WhileASTNode(DecoratedASTNode):
    def __init__(self, condition: DecoratedASTNode, body: DecoratedASTNode):
        super().__init__("While")
        self.condition = condition
        self.body = body

class ForASTNode(DecoratedASTNode):
    def __init__(self, var: str, start: DecoratedASTNode, end: DecoratedASTNode, 
                 body: DecoratedASTNode, is_downto: bool = False):
        super().__init__("For")
        self.var = var
        self.start = start
        self.end = end
        self.body = body
        self.is_downto = is_downto

class RepeatASTNode(DecoratedASTNode):
    def __init__(self, body: List[DecoratedASTNode], condition: DecoratedASTNode):
        super().__init__("Repeat")
        self.body = body
        self.condition = condition

class CaseASTNode(DecoratedASTNode):
    def __init__(self, selector: DecoratedASTNode, cases: List[tuple]):
        super().__init__("Case")
        self.selector = selector
        self.cases = cases  # List of (labels, statement) tuples

class ArrayAccessASTNode(DecoratedASTNode):
    def __init__(self, array: DecoratedASTNode, index: DecoratedASTNode):
        super().__init__("ArrayAccess")
        self.array = array
        self.index = index

class RecordAccessASTNode(DecoratedASTNode):
    def __init__(self, record: DecoratedASTNode, field: str):
        super().__init__("RecordAccess")
        self.record = record
        self.field = field