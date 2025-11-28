from typing import List, Optional
from Parser.ast import *
from Semantic.Visitor.SemanticAnalyzerBase import SemanticAnalyzerBase
from Semantic.Visitor.SemanticError import *
from Semantic.SymbolTable.SymbolTable import ObjectType, DataType
from Semantic.DecoratedAST.DecoratedASTNode import *
from Repository.TokenType import TokenType
from Model.Token import Token

class ArrayAccessVisitor(SemanticAnalyzerBase):
    # Visitor untuk semantic analysis array dan record access
    
    def _parse_identifier_factor(self, node: FactorNode) -> DecoratedASTNode:
        # Parse identifier yang bisa jadi variable, array access, atau record access
        # Node structure: IDENTIFIER | IDENTIFIER[expr] | IDENTIFIER.field | kombinasi
        
        children = node.children
        if not children:
            return None
        
        # Ambil identifier pertama
        first_child = children[0]
        if not isinstance(first_child, Token) or first_child.tokenType != TokenType.IDENTIFIER:
            return None
        
        identifier = first_child.value
        
        # Lookup identifier di symbol table
        idx = self.symbol_table.lookup_identifier(identifier)
        if idx is None:
            raise UndefinedIdentifierError(identifier)
        
        entry = self.symbol_table.tab[idx]
        
        # Buat node awal (VarASTNode)
        result = VarASTNode(identifier)
        result.annotate(
            data_type=entry.type,
            tab_index=idx,
            scope_level=entry.lev
        )
        
        # Parse akses array/record jika ada
        i = 1
        while i < len(children):
            child = children[i]
            
            # Array access: LBRACKET expression RBRACKET
            if isinstance(child, Token) and child.tokenType == TokenType.LBRACKET:
                # Validasi bahwa current result adalah array
                if result.data_type != DataType.ARRAY:
                    raise SemanticError(f"'{identifier}' is not an array")
                
                # Ambil expression untuk index (child berikutnya)
                i += 1
                if i >= len(children):
                    raise SemanticError("Expected array index expression")
                
                # Parse index expression (recursively dari ExpressionVisitor)
                index_expr_node = children[i]
                from Semantic.Visitor.ExpressionVisitor import ExpressionVisitor
                expr_visitor = ExpressionVisitor()
                expr_visitor.symbol_table = self.symbol_table
                index_ast = expr_visitor.visit_expression(index_expr_node)
                
                # Validasi tipe index
                self._validate_array_index(result.data_type, entry.ref, index_ast)
                
                # Get element type dari array
                element_type, element_ref = self._get_array_element_type(entry.ref)
                
                # Buat ArrayAccessASTNode
                result = ArrayAccessASTNode(result, index_ast)
                result.annotate(data_type=element_type)
                
                # Skip RBRACKET
                i += 1
                if i < len(children) and isinstance(children[i], Token) and children[i].tokenType == TokenType.RBRACKET:
                    i += 1
            
            # Record field access: DOT IDENTIFIER
            elif isinstance(child, Token) and child.tokenType == TokenType.DOT:
                # Validasi bahwa current result adalah record
                if result.data_type != DataType.RECORD:
                    raise SemanticError(f"'{identifier}' is not a record")
                
                # Ambil field name (child berikutnya)
                i += 1
                if i >= len(children):
                    raise SemanticError("Expected field name after '.'")
                
                field_token = children[i]
                if not isinstance(field_token, Token) or field_token.tokenType != TokenType.IDENTIFIER:
                    raise SemanticError("Expected field name")
                
                field_name = field_token.value
                
                # Validasi dan ambil field info
                field_type, field_idx = self._get_record_field_info(entry.ref, field_name)
                
                # Buat RecordAccessASTNode
                result = RecordAccessASTNode(result, field_name)
                result.annotate(
                    data_type=field_type,
                    tab_index=field_idx
                )
                
                # Update entry untuk iterasi berikutnya (jika ada nested access)
                entry = self.symbol_table.tab[field_idx]
                i += 1
            else:
                i += 1
        
        return result
    
    def _parse_lvalue(self, children: List) -> DecoratedASTNode:
        # Parse left-hand side of assignment (variable, array access, record access)
        # Digunakan untuk assignment statement: IDENTIFIER := expr
        
        if not children:
            return None
        
        # Ambil identifier pertama
        first_child = children[0]
        if not isinstance(first_child, Token) or first_child.tokenType != TokenType.IDENTIFIER:
            return None
        
        identifier = first_child.value
        
        # Lookup identifier
        idx = self.symbol_table.lookup_identifier(identifier)
        if idx is None:
            raise UndefinedIdentifierError(identifier)
        
        entry = self.symbol_table.tab[idx]
        
        # Validasi bahwa ini adalah lvalue yang valid (variable, bukan constant/procedure/function)
        if entry.obj == ObjectType.CONSTANT:
            raise InvalidAssignmentError(identifier, "cannot assign to constant")
        elif entry.obj not in [ObjectType.VARIABLE, ObjectType.PARAMETER]:
            raise InvalidAssignmentError(identifier, f"cannot assign to {entry.obj.value}")
        
        # Buat node awal
        result = VarASTNode(identifier)
        result.annotate(
            data_type=entry.type,
            tab_index=idx,
            scope_level=entry.lev
        )
        
        # Parse array/record access jika ada
        i = 1
        while i < len(children):
            child = children[i]
            
            # Skip ASSIGN_OPERATOR karena itu bukan bagian dari lvalue
            if isinstance(child, Token) and child.tokenType == TokenType.ASSIGN_OPERATOR:
                break
            
            # Array access
            if isinstance(child, Token) and child.tokenType == TokenType.LBRACKET:
                if result.data_type != DataType.ARRAY:
                    raise SemanticError(f"'{identifier}' is not an array")
                
                # Parse index expression
                i += 1
                if i >= len(children):
                    raise SemanticError("Expected array index")
                
                index_node = children[i]
                from Semantic.Visitor.ExpressionVisitor import ExpressionVisitor
                expr_visitor = ExpressionVisitor()
                expr_visitor.symbol_table = self.symbol_table
                index_ast = expr_visitor.visit_expression(index_node)
                
                # Validasi index
                self._validate_array_index(result.data_type, entry.ref, index_ast)
                
                # Get element type
                element_type, element_ref = self._get_array_element_type(entry.ref)
                
                # Buat array access node
                result = ArrayAccessASTNode(result, index_ast)
                result.annotate(data_type=element_type)
                
                # Skip RBRACKET
                i += 1
                if i < len(children) and isinstance(children[i], Token) and children[i].tokenType == TokenType.RBRACKET:
                    i += 1
            
            # Record field access
            elif isinstance(child, Token) and child.tokenType == TokenType.DOT:
                if result.data_type != DataType.RECORD:
                    raise SemanticError(f"'{identifier}' is not a record")
                
                # Ambil field name
                i += 1
                if i >= len(children):
                    raise SemanticError("Expected field name")
                
                field_token = children[i]
                if not isinstance(field_token, Token) or field_token.tokenType != TokenType.IDENTIFIER:
                    raise SemanticError("Expected field name")
                
                field_name = field_token.value
                
                # Get field info
                field_type, field_idx = self._get_record_field_info(entry.ref, field_name)
                
                # Buat record access node
                result = RecordAccessASTNode(result, field_name)
                result.annotate(
                    data_type=field_type,
                    tab_index=field_idx
                )
                
                # Update entry untuk next iteration
                entry = self.symbol_table.tab[field_idx]
                i += 1
            else:
                i += 1
        
        return result

    def visit_array_access(self, node: ArrayAccessASTNode) -> ArrayAccessASTNode:
        # Visit array access: arr[index]
        # Node sudah dibuat, tinggal validasi dan annotate
        
        # Visit array node (base)
        if hasattr(node.array, 'accept'):
            node.array = node.array.accept(self)
        
        # Visit index node
        if hasattr(node.index, 'accept'):
            node.index = node.index.accept(self)
        
        # Validasi tipe array
        if node.array.data_type != DataType.ARRAY:
            raise SemanticError("Array access on non-array type")
        
        # Validasi tipe index (harus integer)
        if node.index.data_type != DataType.INTEGER:
            raise TypeMismatchError("integer", node.index.data_type.value, "array index")
        
        return node

    def visit_record_access(self, node: RecordAccessASTNode) -> RecordAccessASTNode:
        # Visit record access: rec.field
        
        # Visit record node (base)
        if hasattr(node.record, 'accept'):
            node.record = node.record.accept(self)
        
        # Validasi tipe record
        if node.record.data_type != DataType.RECORD:
            raise SemanticError("Field access on non-record type")
        
        return node

    def _validate_array_index(self, array_type: DataType, array_ref: int, index_node: DecoratedASTNode):
        # Validasi tipe index array (harus integer)
        
        if array_type != DataType.ARRAY:
            raise SemanticError("Not an array type")
        
        # Cek tipe index
        if index_node.data_type != DataType.INTEGER:
            raise TypeMismatchError("integer", index_node.data_type.value, "array index")
        
        # Optional: bisa tambahkan bounds checking jika constant index
        # Untuk sekarang, hanya validasi tipe sudah cukup

    def _validate_record_field(self, record_type: DataType, record_ref: int, field_name: str) -> int:
        # Validasi field ada dalam record, return tab_index field
        
        if record_type != DataType.RECORD:
            raise SemanticError("Not a record type")
        
        # Cari field dalam record block
        if record_ref >= len(self.symbol_table.btab):
            raise SemanticError(f"Invalid record reference: {record_ref}")
        
        record_block = self.symbol_table.btab[record_ref]
        
        # Traverse linked list untuk cari field
        current_idx = record_block.last
        while current_idx != 0:
            entry = self.symbol_table.tab[current_idx]
            if entry.id.lower() == field_name.lower():
                return current_idx
            current_idx = entry.link
        
        # Field tidak ditemukan
        raise SemanticError(f"Record does not have field '{field_name}'")

    def _get_array_element_type(self, array_ref: int) -> tuple:
        # Get element type dari array (dari atab)
        # Return: (element_type, element_ref)
        
        if array_ref < 0 or array_ref >= len(self.symbol_table.atab):
            raise SemanticError(f"Invalid array reference: {array_ref}")
        
        array_entry = self.symbol_table.atab[array_ref]
        return (array_entry.etyp, array_entry.eref)

    def _get_record_field_info(self, record_ref: int, field_name: str) -> tuple:
        # Get field info dari record (dari btab)
        # Return: (field_type, field_tab_index)
        
        # Validasi dan cari field
        field_idx = self._validate_record_field(DataType.RECORD, record_ref, field_name)
        
        # Ambil entry field
        field_entry = self.symbol_table.tab[field_idx]
        
        return (field_entry.type, field_idx)