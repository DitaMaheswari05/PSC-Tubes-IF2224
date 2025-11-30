from typing import List, Optional, Any
from Parser.ast import ASTNode
from Semantic.SymbolTable.SymbolTable import *

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
    
    def to_string(self, indent: int = 0, is_last: bool = True) -> str:
        # Default implementation - override in subclasses untuk format yang lebih baik
        prefix = self._get_prefix(indent, is_last)
        annotations = self._get_annotations()
        return f"{prefix}{self.node_type}{annotations}\n"
    
    def _get_prefix(self, indent: int, is_last: bool) -> str:
        """Generate proper tree line prefix using Unicode box-drawing characters"""
        if indent == 0:
            return ""
        
        lines = []
        for i in range(indent - 1):
            lines.append("│   ")
        
        if is_last:
            lines.append("└─ ")
        else:
            lines.append("├─ ")
        
        return " ".join(lines)
    
    def _get_annotations(self) -> str:
        """Get annotation string with type, tab_index, lev, etc."""
        annotations = []
        if hasattr(self, 'name') and self.name:
            annotations.append(f"'{self.name}'")
        if self.data_type is not None:
            annotations.append(f"type:{self.data_type.name.lower()}")
        if self.tab_index is not None:
            annotations.append(f"tab_index:{self.tab_index}")
        if self.block_index is not None:
            annotations.append(f"block_index:{self.block_index}")
        if self.scope_level is not None:
            annotations.append(f"lev:{self.scope_level}")
        
        if annotations:
            return " -> " + ", ".join(annotations)
        return ""

# Decorated node classes untuk AST yang lebih sederhana
class ProgramASTNode(DecoratedASTNode):
    def __init__(self, name: str):
        super().__init__("Program")
        self.name = name
        self.declarations: List[DecoratedASTNode] = []
        self.block: Optional[DecoratedASTNode] = None
    
    def to_string(self, indent: int = 0, is_last: bool = True) -> str:
        result = f"ProgramNode(name: '{self.name}')\n"
        
        # Declarations section
        if self.declarations:
            result += " ├─ Declarations\n"
            for i, decl in enumerate(self.declarations):
                is_last_decl = (i == len(self.declarations) - 1 and not self.block)
                result += decl.to_string(2, is_last_decl)
        
        # Block section
        if self.block:
            result += " └─ Block"
            # Add block annotations
            if self.block.block_index is not None or self.block.scope_level is not None:
                annotations = []
                if self.block.block_index is not None:
                    annotations.append(f"block_index:{self.block.block_index}")
                if self.block.scope_level is not None:
                    annotations.append(f"lev:{self.block.scope_level}")
                result += " -> " + ", ".join(annotations)
            result += "\n"
            # Print statements inside the block
            for i, stmt in enumerate(self.block.statements):
                is_last_stmt = (i == len(self.block.statements) - 1)
                result += stmt.to_string(2, is_last_stmt)
        
        return result

class VarDeclASTNode(DecoratedASTNode):
    def __init__(self, name: str, var_type: DataType):
        super().__init__("VarDecl")
        self.name = name
        self.var_type = var_type
    
    def to_string(self, indent: int = 0, is_last: bool = True) -> str:
        prefix = self._get_prefix(indent, is_last)
        annotations = []
        if self.tab_index is not None:
            annotations.append(f"tab_index:{self.tab_index}")
        annotations.append(f"type:{self.var_type.name.lower()}")
        if self.scope_level is not None:
            annotations.append(f"lev:{self.scope_level}")
        ann_str = " -> " + ", ".join(annotations) if annotations else ""
        return f"{prefix}VarDecl('{self.name}'){ann_str}\n"

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
    
    def to_string(self, indent: int = 0, is_last: bool = True) -> str:
        # Block node biasanya tidak ditampilkan sendiri, tetapi langsung statements-nya
        # Karena sudah ditampilkan di ProgramNode
        result = ""
        for i, stmt in enumerate(self.statements):
            is_last_stmt = (i == len(self.statements) - 1)
            result += stmt.to_string(indent, is_last_stmt)
        return result

class AssignASTNode(DecoratedASTNode):
    def __init__(self, target: DecoratedASTNode, value: DecoratedASTNode):
        super().__init__("Assign")
        self.target = target
        self.value = value
    
    def _get_value_representation(self, node: DecoratedASTNode) -> str:
        """Extract string representation of value node"""
        # For literal values
        if hasattr(node, 'value'):
            val = node.value
            if isinstance(val, str) and node.node_type == "String":
                return f"'{val}'"
            return str(val)
        # For identifiers
        elif hasattr(node, 'name') and node.node_type == "Var":
            return f"{node.name}"
        # For negative numbers (UnaryOp)
        elif node.node_type == "UnaryOp" and hasattr(node, 'op') and node.op == '-':
            if hasattr(node, 'operand'):
                val = self._get_value_representation(node.operand)
                return f"-{val}"
        # For binary operations
        elif node.node_type == "BinOp" and hasattr(node, 'op'):
            left = self._get_value_representation(node.left) if hasattr(node, 'left') else "?"
            right = self._get_value_representation(node.right) if hasattr(node, 'right') else "?"
            return f"{left}{node.op}{right}"
        # For array access
        elif node.node_type == "ArrayAccess":
            return "..."
        # For function calls
        elif node.node_type in ["FuncCall", "ProcCall"]:
            return "..."
        
        return "..."
    
    def to_string(self, indent: int = 0, is_last: bool = True) -> str:
        target_name = self.target.name if hasattr(self.target, 'name') else str(self.target)
        value_repr = self._get_value_representation(self.value)
        
        prefix = self._get_prefix(indent, is_last)
        # Assignment always has type void
        result = f"{prefix}Assign('{target_name}' := {value_repr}) -> type:void\n"
        
        # Show target with annotations
        target_prefix = self._get_prefix(indent + 1, False)
        target_annotations = []
        if self.target.tab_index is not None:
            target_annotations.append(f"tab_index:{self.target.tab_index}")
        if self.target.data_type is not None:
            target_annotations.append(f"type:{self.target.data_type.name.lower()}")
        target_ann_str = " -> " + ", ".join(target_annotations) if target_annotations else ""
        result += f"{target_prefix}target '{target_name}'{target_ann_str}\n"
        
        # Show value with appropriate formatting
        result += self._format_value_node(self.value, indent + 1, True)
        
        return result
    
    def _format_value_node(self, node: DecoratedASTNode, indent: int, is_last: bool) -> str:
        """Format value node dengan label 'value' di depan"""
        prefix = self._get_prefix(indent, is_last)
        
        if hasattr(node, 'value'):
            # Literal value (Number, String, etc)
            type_str = f"type:{node.data_type.name.lower()}" if node.data_type else ""
            ann_str = f" -> {type_str}" if type_str else ""
            return f"{prefix}value {node.value}{ann_str}\n"
        elif node.node_type == "BinOp":
            # Binary operation
            type_str = f"type:{node.data_type.name.lower()}" if node.data_type else ""
            ann_str = f" -> {type_str}" if type_str else ""
            result = f"{prefix}value BinOp '{node.op}'{ann_str}\n"
            result += node.left.to_string(indent + 1, False)
            result += node.right.to_string(indent + 1, True)
            return result
        elif node.node_type == "UnaryOp":
            # Unary operation
            type_str = f"type:{node.data_type.name.lower()}" if node.data_type else ""
            ann_str = f" -> {type_str}" if type_str else ""
            result = f"{prefix}value UnaryOp '{node.op}'{ann_str}\n"
            result += node.operand.to_string(indent + 1, True)
            return result
        else:
            # For other nodes, just add 'value' label
            return prefix + "value " + node.to_string(0, is_last)[len(self._get_prefix(0, is_last)):]

class VarASTNode(DecoratedASTNode):
    def __init__(self, name: str):
        super().__init__("Var")
        self.name = name
    
    def to_string(self, indent: int = 0, is_last: bool = True) -> str:
        prefix = self._get_prefix(indent, is_last)
        annotations = []
        if self.tab_index is not None:
            annotations.append(f"tab_index:{self.tab_index}")
        if self.data_type is not None:
            annotations.append(f"type:{self.data_type.name.lower()}")
        ann_str = " -> " + ", ".join(annotations) if annotations else ""
        return f"{prefix}'{self.name}'{ann_str}\n"

class NumberASTNode(DecoratedASTNode):
    def __init__(self, value: Any):
        super().__init__("Number")
        self.value = value
        # Tentukan tipe berdasarkan nilai
        if isinstance(value, int):
            self.data_type = DataType.INTEGER
        elif isinstance(value, float):
            self.data_type = DataType.REAL
    
    def to_string(self, indent: int = 0, is_last: bool = True) -> str:
        prefix = self._get_prefix(indent, is_last)
        type_str = f"type:{self.data_type.name.lower()}" if self.data_type else ""
        ann_str = f" -> {type_str}" if type_str else ""
        return f"{prefix}{self.value}{ann_str}\n"

class StringASTNode(DecoratedASTNode):
    def __init__(self, value: str):
        super().__init__("String")
        self.value = value
        self.data_type = DataType.STRING
    
    def to_string(self, indent: int = 0, is_last: bool = True) -> str:
        prefix = self._get_prefix(indent, is_last)
        return f"{prefix}\"{self.value}\" -> type:string\n"

class CharASTNode(DecoratedASTNode):
    def __init__(self, value: str):
        super().__init__("Char")
        self.value = value
        self.data_type = DataType.CHAR
    
    def to_string(self, indent: int = 0, is_last: bool = True) -> str:
        prefix = self._get_prefix(indent, is_last)
        return f"{prefix}'{self.value}' -> type:char\n"

class BooleanASTNode(DecoratedASTNode):
    def __init__(self, value: bool):
        super().__init__("Boolean")
        self.value = value
        self.data_type = DataType.BOOLEAN
    
    def to_string(self, indent: int = 0, is_last: bool = True) -> str:
        prefix = self._get_prefix(indent, is_last)
        value_str = "true" if self.value else "false"
        return f"{prefix}{value_str} -> type:boolean\n"

class BinOpASTNode(DecoratedASTNode):
    def __init__(self, op: str, left: DecoratedASTNode, right: DecoratedASTNode):
        super().__init__("BinOp")
        self.op = op
        self.left = left
        self.right = right
    
    def to_string(self, indent: int = 0, is_last: bool = True) -> str:
        prefix = self._get_prefix(indent, is_last)
        type_str = f"type:{self.data_type.name.lower()}" if self.data_type else ""
        ann_str = f" -> {type_str}" if type_str else ""
        result = f"{prefix}BinOp '{self.op}'{ann_str}\n"
        
        # Show left and right operands
        result += self.left.to_string(indent + 1, False)
        result += self.right.to_string(indent + 1, True)
        
        return result

class UnaryOpASTNode(DecoratedASTNode):
    def __init__(self, op: str, operand: DecoratedASTNode):
        super().__init__("UnaryOp")
        self.op = op
        self.operand = operand
    
    def to_string(self, indent: int = 0, is_last: bool = True) -> str:
        prefix = self._get_prefix(indent, is_last)
        type_str = f"type:{self.data_type.name.lower()}" if self.data_type else ""
        ann_str = f" -> {type_str}" if type_str else ""
        result = f"{prefix}UnaryOp '{self.op}'{ann_str}\n"
        
        result += self.operand.to_string(indent + 1, True)
        
        return result

class ProcCallASTNode(DecoratedASTNode):
    def __init__(self, name: str, args: List[DecoratedASTNode]):
        super().__init__("ProcCall")
        self.name = name
        self.args = args
        self.is_predefined = False  # Flag untuk menandai predefined procedure
    
    def to_string(self, indent: int = 0, is_last: bool = True) -> str:
        prefix = self._get_prefix(indent, is_last)
        arg_count = len(self.args) if self.args else 0
        
        # Build annotations
        annotations = []
        if self.tab_index is not None:
            annotations.append(f"tab_index:{self.tab_index}")
        if self.is_predefined:
            annotations.append("predefined")
        
        ann_str = " -> " + ", ".join(annotations) if annotations else ""
        
        result = f"{prefix}{self.name}(args: {arg_count}){ann_str}\n"
        
        # Show arguments if any
        if self.args:
            for i, arg in enumerate(self.args):
                is_last_arg = (i == len(self.args) - 1)
                result += arg.to_string(indent + 1, is_last_arg)
        
        return result

class FuncCallASTNode(DecoratedASTNode):
    def __init__(self, name: str, args: List[DecoratedASTNode]):
        super().__init__("FuncCall")
        self.name = name
        self.args = args
    
    def to_string(self, indent: int = 0, is_last: bool = True) -> str:
        prefix = self._get_prefix(indent, is_last)
        type_str = f"type:{self.data_type.name.lower()}" if self.data_type else ""
        ann_str = f" -> {type_str}" if type_str else ""
        arg_count = len(self.args) if self.args else 0
        result = f"{prefix}{self.name}(args: {arg_count}){ann_str}\n"
        
        # Show arguments if any
        if self.args:
            for i, arg in enumerate(self.args):
                is_last_arg = (i == len(self.args) - 1)
                result += arg.to_string(indent + 1, is_last_arg)
        
        return result

class IfASTNode(DecoratedASTNode):
    def __init__(self, condition: DecoratedASTNode, then_stmt: DecoratedASTNode, 
                 else_stmt: Optional[DecoratedASTNode] = None):
        super().__init__("If")
        self.condition = condition
        self.then_stmt = then_stmt
        self.else_stmt = else_stmt
    
    def to_string(self, indent: int = 0, is_last: bool = True) -> str:
        prefix = self._get_prefix(indent, is_last)
        result = f"{prefix}If-Then-Else -> type:void\n"
        
        # Show condition
        cond_prefix = self._get_prefix(indent + 1, False)
        result += f"{cond_prefix}condition\n"
        result += self.condition.to_string(indent + 2, True)
        
        # Show then statement
        then_prefix = self._get_prefix(indent + 1, self.else_stmt is None)
        result += f"{then_prefix}then\n"
        result += self.then_stmt.to_string(indent + 2, True)
        
        # Show else statement if present
        if self.else_stmt:
            else_prefix = self._get_prefix(indent + 1, True)
            result += f"{else_prefix}else\n"
            result += self.else_stmt.to_string(indent + 2, True)
        
        return result

class WhileASTNode(DecoratedASTNode):
    def __init__(self, condition: DecoratedASTNode, body: DecoratedASTNode):
        super().__init__("While")
        self.condition = condition
        self.body = body
    
    def to_string(self, indent: int = 0, is_last: bool = True) -> str:
        prefix = self._get_prefix(indent, is_last)
        result = f"{prefix}While-Do -> type:void\n"
        
        # Show condition
        cond_prefix = self._get_prefix(indent + 1, False)
        result += f"{cond_prefix}condition\n"
        result += self.condition.to_string(indent + 2, True)
        
        # Show body
        body_prefix = self._get_prefix(indent + 1, True)
        result += f"{body_prefix}body\n"
        result += self.body.to_string(indent + 2, True)
        
        return result

class ForASTNode(DecoratedASTNode):
    def __init__(self, var: str, start: DecoratedASTNode, end: DecoratedASTNode, 
                 body: DecoratedASTNode, is_downto: bool = False):
        super().__init__("For")
        self.var = var
        self.start = start
        self.end = end
        self.body = body
        self.is_downto = is_downto
    
    def to_string(self, indent: int = 0, is_last: bool = True) -> str:
        prefix = self._get_prefix(indent, is_last)
        direction = "downto" if self.is_downto else "to"
        result = f"{prefix}For '{self.var}' {direction} -> type:void\n"
        
        # Show range
        start_prefix = self._get_prefix(indent + 1, False)
        result += f"{start_prefix}start\n"
        result += self.start.to_string(indent + 2, True)
        
        end_prefix = self._get_prefix(indent + 1, False)
        result += f"{end_prefix}end\n"
        result += self.end.to_string(indent + 2, True)
        
        # Show body
        body_prefix = self._get_prefix(indent + 1, True)
        result += f"{body_prefix}body\n"
        result += self.body.to_string(indent + 2, True)
        
        return result

class RepeatASTNode(DecoratedASTNode):
    def __init__(self, body: List[DecoratedASTNode], condition: DecoratedASTNode):
        super().__init__("Repeat")
        self.body = body
        self.condition = condition
    
    def to_string(self, indent: int = 0, is_last: bool = True) -> str:
        prefix = self._get_prefix(indent, is_last)
        result = f"{prefix}Repeat-Until -> type:void\n"
        
        # Show body statements
        for i, stmt in enumerate(self.body):
            is_last_stmt = (i == len(self.body) - 1)
            result += stmt.to_string(indent + 1, is_last_stmt)
        
        # Show condition
        until_prefix = self._get_prefix(indent + 1, True)
        result += f"{until_prefix}until\n"
        result += self.condition.to_string(indent + 2, True)
        
        return result

class CaseASTNode(DecoratedASTNode):
    def __init__(self, selector: DecoratedASTNode, cases: List[tuple]):
        super().__init__("Case")
        self.selector = selector
        self.cases = cases  # List of (labels, statement) tuples
    
    def to_string(self, indent: int = 0, is_last: bool = True) -> str:
        prefix = self._get_prefix(indent, is_last)
        result = f"{prefix}Case-Of -> type:void\n"
        
        # Show selector
        sel_prefix = self._get_prefix(indent + 1, False)
        result += f"{sel_prefix}selector\n"
        result += self.selector.to_string(indent + 2, True)
        
        # Show cases
        for i, (labels, stmt) in enumerate(self.cases):
            is_last_case = (i == len(self.cases) - 1)
            label_str = ", ".join(str(l) for l in labels) if isinstance(labels, list) else str(labels)
            case_prefix = self._get_prefix(indent + 1, is_last_case)
            result += f"{case_prefix}case {label_str}\n"
            result += stmt.to_string(indent + 2, True)
        
        return result

class ArrayAccessASTNode(DecoratedASTNode):
    def __init__(self, array: DecoratedASTNode, index: DecoratedASTNode):
        super().__init__("ArrayAccess")
        self.array = array
        self.index = index
    
    def to_string(self, indent: int = 0, is_last: bool = True) -> str:
        prefix = self._get_prefix(indent, is_last)
        type_str = f"type:{self.data_type.name.lower()}" if self.data_type else ""
        ann_str = f" -> {type_str}" if type_str else ""
        result = f"{prefix}ArrayAccess[index]{ann_str}\n"
        
        # Show array and index
        result += self.array.to_string(indent + 1, False)
        result += self.index.to_string(indent + 1, True)
        
        return result

class RecordAccessASTNode(DecoratedASTNode):
    def __init__(self, record: DecoratedASTNode, field: str):
        super().__init__("RecordAccess")
        self.record = record
        self.field = field
    
    def to_string(self, indent: int = 0, is_last: bool = True) -> str:
        prefix = self._get_prefix(indent, is_last)
        type_str = f"type:{self.data_type.name.lower()}" if self.data_type else ""
        ann_str = f" -> {type_str}" if type_str else ""
        result = f"{prefix}RecordAccess.{self.field}{ann_str}\n"
        
        result += self.record.to_string(indent + 1, True)
        
        return result