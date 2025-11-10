# Abstract Syntax Tree

from typing import List, Any
from Model.Token import Token

class ASTNode:
    def __init__(self, node_type: str):
        self.node_type = node_type
        self.children: List[Any] = []
    
    def add_child(self, child):
        if child is not None:
            self.children.append(child)
    
    def to_string(self, indent: int = 0) -> str:
        prefix = "│   " * indent
        if indent > 0:
            prefix = "│   " * (indent - 1) + "├── "
        
        result = f"{prefix}<{self.node_type}>\n"
        
        for i, child in enumerate(self.children):
            is_last = (i == len(self.children) - 1)
            
            if isinstance(child, ASTNode):
                result += child.to_string(indent + 1)
            elif isinstance(child, Token):
                child_prefix = "│   " * indent + "├── "
                if is_last:
                    child_prefix = "│   " * indent + "└── "
                result += f"{child_prefix}{child.getType().name}({child.getLexeme()})\n"
            else:
                child_prefix = "│   " * indent + "├── "
                if is_last:
                    child_prefix = "│   " * indent + "└── "
                result += f"{child_prefix}{str(child)}\n"
        
        return result
    
    def __str__(self):
        return self.to_string() 
    
class ProgramNode(ASTNode):
    # node untuk <program>
    def __init__(self):
        super().__init__("program")

class ProgramHeaderNode(ASTNode):
    # node untuk <program-header>
    def __init__(self):
        super().__init__("program-header")

class DeclarationPartNode(ASTNode):
    # node untuk <declaration-part>
    def __init__(self):
        super().__init__("declaration-part")

class ConstDeclarationNode(ASTNode):
    # node untuk <const-declaration>
    def __init__(self):
        super().__init__("const-declaration")
        
class TypeDeclarationNode(ASTNode):
    # node untuk <type-declaration>
    def __init__(self):
        super().__init__("type-declaration")
        
class VarDeclarationNode(ASTNode):
    # node untuk <var-declaration>
    def __init__(self):
        super().__init__("var-declaration")

class IdentifierListNode(ASTNode):
    # node untuk <identifier-list>
    def __init__(self):
        super().__init__("identifier-list")

class TypeNode(ASTNode):
    # node untuk <type>
    def __init__(self):
        super().__init__("type")

class ArrayTypeNode(ASTNode):
    # node untuk <array-type>
    def __init__(self):
        super().__init__("array-type")

class RangeNode(ASTNode):
    # node untuk <range>
    def __init__(self):
        super().__init__("range")
        
class SubrangeDeclarationNode(ASTNode):
    # node untuk <subrange-declaration>
    def __init__(self):
        super().__init__("subrange-declaration")

class ProcedureDeclarationNode(ASTNode):
    # node untuk <procedure-declaration>
    def __init__(self):
        super().__init__("procedure-declaration")

class FunctionDeclarationNode(ASTNode):
    # node untuk <function-declaration>
    def __init__(self):
        super().__init__("function-declaration")

class FormalParameterListNode(ASTNode):
    # node untuk <formal-parameter-list>
    def __init__(self):
        super().__init__("formal-parameter-list")

class CompoundStatementNode(ASTNode):
    # node untuk <compound-statement>
    def __init__(self):
        super().__init__("compound-statement")

class StatementListNode(ASTNode):
    # node untuk <statement-list>
    def __init__(self):
        super().__init__("statement-list")

class AssignmentStatementNode(ASTNode):
    # node untuk <assignment-statement>
    def __init__(self):
        super().__init__("assignment-statement")

class IfStatementNode(ASTNode):
    # node untuk <if-statement>
    def __init__(self):
        super().__init__("if-statement")

class WhileStatementNode(ASTNode):
    # node untuk <while-statement>
    def __init__(self):
        super().__init__("while-statement")

class ForStatementNode(ASTNode):
    # node untuk <for-statement>
    def __init__(self):
        super().__init__("for-statement")

class CallStatementNode(ASTNode):
    # node gabungan untuk procedure-call dan function-call
    def __init__(self, is_function=False):
        call_type = "function-call" if is_function else "procedure-call"
        super().__init__(call_type)

class ParameterListNode(ASTNode):
    # node untuk <parameter-list>
    def __init__(self):
        super().__init__("parameter-list")

class ExpressionNode(ASTNode):
    # node untuk <expression>
    def __init__(self):
        super().__init__("expression")

class SimpleExpressionNode(ASTNode):
    # node untuk <simple-expression>
    def __init__(self):
        super().__init__("simple-expression")

class TermNode(ASTNode):
    # node untuk <term>
    def __init__(self):
        super().__init__("term")
        
class FactorNode(ASTNode):
    # node untuk <factor>
    def __init__(self):
        super().__init__("factor")

class RelationalOperatorNode(ASTNode):
    # node untuk <relational-operator>
    def __init__(self):
        super().__init__("relational-operator")

class AdditiveOperatorNode(ASTNode):
    # node untuk <additive-operator>
    def __init__(self):
        super().__init__("additive-operator")

class MultiplicativeOperatorNode(ASTNode):
    # node untuk <multiplicative-operator>
    def __init__(self):
        super().__init__("multiplicative-operator")