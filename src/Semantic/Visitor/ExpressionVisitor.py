# ini template aja, atur-atur sesuai kebutuhan
from Parser.ast import *
from src.Semantic.Visitor.SemanticAnalyzerBase import SemanticAnalyzerBase
from src.Semantic.Visitor.SemanticError import *
from src.Semantic.SymbolTable.SymbolTable import *
from src.Semantic.DecoratedAST.DecoratedASTNode import *
from src.Semantic.Visitor.ProcFuncVisitor import ProcFuncVisitor
from Repository.TokenType import TokenType
from Model.Token import Token

class ExpressionVisitor(SemanticAnalyzerBase):
    # Visitor untuk semantic analysis expression nodes
    
    def visit_expression(self, node: ExpressionNode) -> DecoratedASTNode:
        # Visit expression
        # expression -> simple-expression (relop simple-expression)?
        
        left = None
        right = None
        operator = None
        
        for child in node.children:
            if isinstance(child, SimpleExpressionNode):
                if left is None:
                    left = self.visit_simple_expression(child)
                else:
                    right = self.visit_simple_expression(child)
            elif isinstance(child, Token) and child.token_type == TokenType.RELATIONAL_OPERATOR:
                operator = child.value
            
        if operator and right:
            if left.data_type != right.data_type:
                 if not ((left.data_type == DataType.REAL and right.data_type == DataType.INTEGER) or
                        (left.data_type == DataType.INTEGER and right.data_type == DataType.REAL)):
                    raise SemanticError(
                        f"Type mismatch in relational operation: {left.data_type.name} {operator} {right.data_type.name}"
                    )
        
            ast_node = BinOpASTNode(operator, left, right)
            ast_node.annotate = DataType.BOOLEAN
            return ast_node
   
        return left
    
    def visit_simple_expression(self, node: SimpleExpressionNode) -> DecoratedASTNode:
        # Visit simple expression
        # simple-expression -> (sign)? term (addop term)*
        
        terms = []
        operators = []
        has_unary = False
        unary_op = False
        
        for child in node.children:
            if isinstance(child, TermNode):
                terms.append(self.visit_term(child))
            elif isinstance(child, Token):
                if child.tokenType == TokenType.ARITHMETIC_OPERATOR:
                    if not terms: # Unary operator
                        has_unary = True
                        unary_op = child.value
                    else: # Binary operator
                        operators.append(child.value)
                elif child.tokenType == TokenType.LOGICAL_OPERATOR and child.value == "atau":
                    operators.append(child.value)
        
        #  Handle unary operator
        if has_unary and terms:
            terms[0] = UnaryOpASTNode(unary_op, terms[0])
            terms[0].annotate(data_type=terms[0].data_type)
            
        # Bangun expression tree dari kiri ke kanan
        result = terms[0]
        for i, op in enumerate(operators):
            right = terms[i + 1]
            result = self._create_binary_op(op, result, right)
        
        return result  
    
    def visit_term(self, node: TermNode) -> DecoratedASTNode:
        # Visit term
        # term -> factor (mulop factor)*
        
        factors = []
        operators = []
        
        for child in node.children:
            if isinstance(child, FactorNode):
                factors.append(self.visit_factor(child))
            elif isinstance(child, Token):
                if child.token_type == TokenType.ARITHMETIC_OPERATOR:
                    operators.append(child.value)
                elif child.token_type == TokenType.LOGICAL_OPERATOR and child.value == "dan":  
                    operators.append(child.value)
        
        # Bangun expression tree
        result = factors[0]
        for i, op in enumerate(operators):
            right = factors[i + 1]
            result = self._create_binary_op(op, result, right)
            
        return result
    
    def visit_factor(self, node: FactorNode) -> DecoratedASTNode:
        # Visit factor
        # factor -> NUMBER | STRING | CHAR | IDENTIFIER | function-call | 
        #           array-access | record-access | (expression) | NOT factor
        
        if not node.children:
            raise SemanticError("Empty factor node")
        
        first_child = node.children[0]
        
        # NUMBER
        if isinstance(first_child, Token) and first_child.tokenType == TokenType.NUMBER:
            value = first_child.value
            if '.' in str(value):
                return NumberASTNode(float(value))
            else:
                return NumberASTNode(int(value))
        
        # STRING
        elif isinstance(first_child, Token) and first_child.tokenType == TokenType.STRING_LITERAL:
            return StringASTNode(first_child.value)
        
        # CHAR
        elif isinstance(first_child, Token) and first_child.tokenType == TokenType.CHAR_LITERAL:
            return CharASTNode(first_child.value)
        
        # BOOLEAN (true/false)
        elif isinstance(first_child, Token) and first_child.tokenType == TokenType.KEYWORD:
            if first_child.value.lower() in ["true", "false"]:
                return BooleanASTNode(first_child.value.lower() == "true")
        
        # NOT factor
        elif isinstance(first_child, Token) and first_child.tokenType == TokenType.LOGICAL_OPERATOR and first_child.value == "tidak":
            operand = self.visit_factor(node.children[1])
            if operand.data_type != DataType.BOOLEAN:
                raise SemanticError(f"NOT operator requires boolean operand, got {operand.data_type.name}")
            ast_node = UnaryOpASTNode("tidak", operand)
            ast_node.annotate(data_type=DataType.BOOLEAN)
            return ast_node
        
        # (expression)
        elif isinstance(first_child, Token) and first_child.tokenType == TokenType.LPARENTHESIS:
            return self.visit_expression(node.children[1])
        
        # IDENTIFIER (variable, function call, array access, record access)
        elif isinstance(first_child, Token) and first_child.tokenType == TokenType.IDENTIFIER:
            from Semantic.Visitor.ArrayAccessVisitor import ArrayAccessVisitor
            array_visitor = ArrayAccessVisitor()
            array_visitor.symbol_table = self.symbol_table
            array_visitor.errors = self.errors
            return array_visitor._parse_identifier_factor(node)
        
        # CallStatementNode (function call)
        elif isinstance(first_child, CallStatementNode):
            call_visitor = ProcFuncVisitor()
            call_visitor.symbol_table = self.symbol_table
            call_visitor.errors = self.errors
            return call_visitor.visit_function_call(first_child)
        
        raise SemanticError(f"Unknown factor type")
    
    def visit_parameter_list(self, node: ParameterListNode) -> list:
        # Visit parameter list
        
        params = []
        for child in node.children:
            if isinstance(child, ExpressionNode):
                param = self.visit_expression(child)
                params.append(param)
        return params
    
    def _create_binary_op(self, op: str, left: DecoratedASTNode, right: DecoratedASTNode) -> BinOpASTNode:
        # Create binary operation node dengan type checking
        result_type = self._check_type_compatibility(left.data_type, right.data_type, op)
        
        ast_node = BinOpASTNode(op, left, right)
        ast_node.annotate(data_type=result_type)
        
        return ast_node

    def _check_type_compatibility(self, left_type: DataType, right_type: DataType, op: str) -> DataType:
        # Cek kompatibilitas tipe untuk suatu operasi dan kembalikan tipe hasilnya
        
        if op in ['+', '-', '*', '/', 'bagi', 'mod']:
            # Cek apakah kedua operand bertipe numerik
            if left_type not in [DataType.INTEGER, DataType.REAL]:
                raise InvalidOperationError(op, f"operand kiri bertipe {left_type.name}, seharusnya bertipe numerik")
            if right_type not in [DataType.INTEGER, DataType.REAL]:
                raise InvalidOperationError(op, f"operand kanan bertipe {right_type.name}, seharusnya bertipe numerik")
            
            # Operasi bagi (integer division) dan modulo mengembalikan integer
            if op in ['bagi', 'mod']:
                return DataType.INTEGER
            
            # Operasi pembagian selalu menghasilkan real
            if op == '/':
                return DataType.REAL
            
            # Untuk +, -, *
            # Jika salah satu operand adalah REAL, hasilnya REAL
            if left_type == DataType.REAL or right_type == DataType.REAL:
                return DataType.REAL
            
            # Jika keduanya INTEGER
            return DataType.INTEGER
        
        # Operator logika: dan, atau
        elif op in ['dan', 'atau']:
            if left_type != DataType.BOOLEAN:
                raise TypeMismatchError("boolean", left_type.name, f"operasi logika '{op}'")
            if right_type != DataType.BOOLEAN:
                raise TypeMismatchError("boolean", right_type.name, f"operasi logika '{op}'")
            
            return DataType.BOOLEAN
        
        # Operator relasional: =, <>, <, >, <=, >=
        elif op in ['=', '<>', '<', '>', '<=', '>=']:
            # Perbandingan jika kedua tipe sama
            if left_type == right_type:
                return DataType.BOOLEAN
            
            # Perbandingan INTEGER dan REAL
            if (left_type == DataType.INTEGER and right_type == DataType.REAL) or (left_type == DataType.REAL and right_type == DataType.INTEGER):
                return DataType.BOOLEAN
            
            # Untuk tipe lain, harus benar-benar sama
            raise TypeMismatchError(
                left_type.name, 
                right_type.name, 
                f"operasi relasional '{op}'"
            )
        
        # Concat string
        elif op == '+' and left_type == DataType.STRING and right_type == DataType.STRING:
            return DataType.STRING
        
        # Operator tidak dikenal
        else:
            raise InvalidOperationError(op, f"{left_type.name} dan {right_type.name}")


    def _infer_expression_type(self, node: DecoratedASTNode) -> DataType:
        # Menentukan tipe dari sebuah node ekspresi
        
        # Jika node sudah memiliki anotasi tipe, langsung kembalikan itu
        if node.data_type is not None:
            return node.data_type
        
        # Tentukan tipe berdasarkan jenis node
        if isinstance(node, NumberASTNode):
            # Cek apakah integer atau real berdasarkan nilai literal
            if isinstance(node.value, int):
                return DataType.INTEGER
            elif isinstance(node.value, float):
                return DataType.REAL
            return DataType.INTEGER
        
        elif isinstance(node, StringASTNode):
            return DataType.STRING
        
        elif isinstance(node, CharASTNode):
            return DataType.CHAR
        
        elif isinstance(node, BooleanASTNode):
            return DataType.BOOLEAN
        
        elif isinstance(node, VarASTNode):
            # Cari variabel di symbol table
            if node.tab_index is not None:
                entry = self.symbol_table.tab[node.tab_index]
                return entry.type
            return DataType.VOID
        
        elif isinstance(node, BinOpASTNode):
            # Tentukan tipe dari kedua operand
            left_type = self._infer_expression_type(node.left)
            right_type = self._infer_expression_type(node.right)
            
            # Cek kompatibilitas dan kembalikan tipe hasil
            return self._check_type_compatibility(left_type, right_type, node.op)
        
        elif isinstance(node, UnaryOpASTNode):
            operand_type = self._infer_expression_type(node.operand)
            
            # Unary minus/plus: hanya untuk tipe numerik
            if node.op in ['+', '-']:
                if operand_type not in [DataType.INTEGER, DataType.REAL]:
                    raise InvalidOperationError(
                        f"unary {node.op}", 
                        f"{operand_type.name}"
                    )
                return operand_type
            
            # Unary not: hanya untuk boolean
            elif node.op == 'tidak':
                if operand_type != DataType.BOOLEAN:
                    raise TypeMismatchError(
                        "boolean", 
                        operand_type.name, 
                        "operasi unary NOT"
                    )
                return DataType.BOOLEAN
            
            return operand_type
        
        elif isinstance(node, FuncCallASTNode):
            # Pemanggilan fungsi mengembalikan tipe yang dideklarasikan
            if node.tab_index is not None:
                entry = self.symbol_table.tab[node.tab_index]
                return entry.type
            return DataType.VOID
        
        elif isinstance(node, ArrayAccessASTNode):
            # Akses array mengembalikan tipe elemen
            # Tipe elemen seharusnya sudah ditentukan dalam analisis semantik
            if node.data_type is not None:
                return node.data_type
            return DataType.VOID
        
        elif isinstance(node, RecordAccessASTNode):
            # Akses field record mengembalikan tipe field
            if node.data_type is not None:
                return node.data_type
            return DataType.VOID
        
        # Default: kembalikan VOID jika tidak bisa menentukan tipe
        return DataType.VOID
