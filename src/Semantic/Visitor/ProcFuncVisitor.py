from typing import List, Optional
from Parser.ast import *
from Semantic.Visitor.SemanticAnalyzerBase import SemanticAnalyzerBase
from Semantic.Visitor.SemanticError import *
from Semantic.SymbolTable.SymbolTable import *
from Semantic.DecoratedAST.DecoratedASTNode import *
from Repository.TokenType import TokenType
from Model.Token import Token

class ProcFuncVisitor(SemanticAnalyzerBase):
    # Visitor untuk semantic analysis procedure dan function call
    
    def visit_procedure_call(self, node: CallStatementNode) -> ProcCallASTNode:
        # Visit procedure call
        # Node structure: IDENTIFIER/KEYWORD LPARENTHESIS [ParameterListNode] RPARENTHESIS
        
        children = node.children
        if not children:
            raise SemanticError("Empty procedure call node")
        
        # Ambil nama procedure (bisa IDENTIFIER atau KEYWORD untuk built-in)
        name_token = children[0]
        if isinstance(name_token, Token):
            proc_name = name_token.value
        else:
            raise SemanticError("Expected procedure name")
        
        # Parse arguments jika ada
        args: List[DecoratedASTNode] = []
        for child in children:
            if isinstance(child, ParameterListNode):
                # Parse setiap argument dalam parameter list
                from Semantic.Visitor.ExpressionVisitor import ExpressionVisitor
                expr_visitor = ExpressionVisitor()
                expr_visitor.symbol_table = self.symbol_table
                
                for param_child in child.children:
                    # Skip COMMA tokens
                    if isinstance(param_child, Token) and param_child.tokenType == TokenType.COMMA:
                        continue
                    
                    # Parse expression untuk setiap parameter
                    if isinstance(param_child, ExpressionNode):
                        arg_ast = expr_visitor.visit_expression(param_child)
                        args.append(arg_ast)
        
        # Cek apakah built-in procedure
        builtin_procs = ['writeln', 'write', 'readln', 'read']
        if proc_name.lower() in builtin_procs:
            self._check_builtin_procedure(proc_name, args)
            
            # Buat ProcCallASTNode untuk built-in
            ast_node = ProcCallASTNode(proc_name, args)
            ast_node.annotate(data_type=DataType.VOID)
            return ast_node
        
        # Lookup procedure di symbol table
        idx = self.symbol_table.lookup_identifier(proc_name)
        if idx is None:
            raise UndefinedIdentifierError(proc_name)
        
        entry = self.symbol_table.tab[idx]
        
        # Validasi bahwa ini adalah procedure
        if entry.obj != ObjectType.PROCEDURE:
            raise SemanticError(f"'{proc_name}' is not a procedure")
        
        # Validasi arguments
        self._validate_call_arguments(proc_name, idx, args)
        
        # Buat ProcCallASTNode
        ast_node = ProcCallASTNode(proc_name, args)
        ast_node.annotate(
            data_type=DataType.VOID,
            tab_index=idx,
            scope_level=entry.lev
        )
        
        return ast_node
    
    def visit_function_call(self, node: CallStatementNode) -> FuncCallASTNode:
        # Visit function call (dipanggil dari dalam expression)
        # Structure sama dengan procedure call tapi return type nya bukan VOID
        
        children = node.children
        if not children:
            raise SemanticError("Empty function call node")
        
        # Ambil nama function
        name_token = children[0]
        if isinstance(name_token, Token):
            func_name = name_token.value
        else:
            raise SemanticError("Expected function name")
        
        # Parse arguments
        args: List[DecoratedASTNode] = []
        for child in children:
            if isinstance(child, ParameterListNode):
                from Semantic.Visitor.ExpressionVisitor import ExpressionVisitor
                expr_visitor = ExpressionVisitor()
                expr_visitor.symbol_table = self.symbol_table
                
                for param_child in child.children:
                    if isinstance(param_child, Token) and param_child.tokenType == TokenType.COMMA:
                        continue
                    
                    if isinstance(param_child, ExpressionNode):
                        arg_ast = expr_visitor.visit_expression(param_child)
                        args.append(arg_ast)
        
        # Lookup function
        idx = self.symbol_table.lookup_identifier(func_name)
        if idx is None:
            raise UndefinedIdentifierError(func_name)
        
        entry = self.symbol_table.tab[idx]
        
        # Validasi bahwa ini adalah function
        if entry.obj != ObjectType.FUNCTION:
            raise SemanticError(f"'{func_name}' is not a function")
        
        # Validasi arguments
        self._validate_call_arguments(func_name, idx, args)
        
        # Get return type
        return_type = self._get_function_return_type(idx)
        
        # Buat FuncCallASTNode
        ast_node = FuncCallASTNode(func_name, args)
        ast_node.annotate(
            data_type=return_type,
            tab_index=idx,
            scope_level=entry.lev
        )
        
        return ast_node

    def _validate_call_arguments(self, name: str, tab_index: int, args: List[DecoratedASTNode]):
        # Validasi:
        # - Jumlah argumen sesuai
        # - Tipe argumen kompatibel dengan parameter
        # - By-reference parameter (var) hanya menerima lvalue
        
        # Get parameter list
        params = self._get_parameter_list(tab_index)
        
        # Cek jumlah parameter
        if len(args) != len(params):
            raise ParameterError(name, len(params), len(args))
        
        # Validasi setiap argument dengan parameter
        for i, (param_name, param_type, is_var_param) in enumerate(params):
            arg = args[i]
            
            # Cek tipe compatibility
            if arg.data_type != param_type:
                # Allow beberapa implicit conversion
                # Integer ke Real
                if param_type == DataType.REAL and arg.data_type == DataType.INTEGER:
                    pass  # OK
                else:
                    raise TypeMismatchError(
                        param_type.value,
                        arg.data_type.value,
                        f"parameter {i+1} of '{name}'"
                    )
            
            # Jika var parameter, harus lvalue (variable)
            if is_var_param:
                # Cek apakah arg adalah lvalue (VarASTNode, ArrayAccessASTNode, RecordAccessASTNode)
                if not isinstance(arg, (VarASTNode, ArrayAccessASTNode, RecordAccessASTNode)):
                    raise SemanticError(
                        f"Parameter {i+1} of '{name}' is var parameter, requires lvalue"
                    )

    def _get_parameter_list(self, tab_index: int) -> List[tuple]:
        # Get list parameter dari procedure/function
        # Return: [(param_name, param_type, is_var_param), ...]
        
        entry = self.symbol_table.tab[tab_index]
        
        # ref menunjuk ke block entry untuk procedure/function
        if entry.ref <= 0 or entry.ref >= len(self.symbol_table.btab):
            return []  # Tidak ada parameter
        
        block_entry = self.symbol_table.btab[entry.ref]
        
        # lpar menunjuk ke parameter terakhir dalam linked list
        # Traverse dari lpar untuk mengumpulkan semua parameter
        params = []
        current_idx = block_entry.lpar
        
        # Kumpulkan parameter dalam reverse order (karena linked list)
        param_indices = []
        while current_idx != 0:
            param_indices.append(current_idx)
            param_entry = self.symbol_table.tab[current_idx]
            current_idx = param_entry.link
        
        # Balik urutan agar sesuai dengan deklarasi
        param_indices.reverse()
        
        # Buat list parameter
        for idx in param_indices:
            param_entry = self.symbol_table.tab[idx]
            if param_entry.obj == ObjectType.PARAMETER:
                # nrm=0 berarti var parameter (by reference)
                # nrm=1 berarti value parameter
                is_var_param = (param_entry.nrm == 0)
                params.append((param_entry.id, param_entry.type, is_var_param))
        
        return params

    def _check_builtin_procedure(self, name: str, args: List[DecoratedASTNode]):
        # Validasi built-in procedures: writeln, write, readln, read
        # - writeln/write: bisa variadic, accept any type
        # - readln/read: hanya variable (lvalue), dan harus tipe yang bisa dibaca
        
        name_lower = name.lower()
        
        if name_lower in ['writeln', 'write']:
            # writeln/write: accept any type, any number of arguments
            # No specific validation needed untuk writeln/write
            pass
        
        elif name_lower in ['readln', 'read']:
            # readln/read: harus lvalue dan tipe yang bisa dibaca
            for i, arg in enumerate(args):
                # Cek apakah lvalue
                if not isinstance(arg, (VarASTNode, ArrayAccessASTNode, RecordAccessASTNode)):
                    raise SemanticError(
                        f"Argument {i+1} of '{name}' must be a variable"
                    )
                
                # Cek tipe yang bisa dibaca (integer, real, char, string)
                readable_types = [DataType.INTEGER, DataType.REAL, DataType.CHAR, DataType.STRING]
                if arg.data_type not in readable_types:
                    raise SemanticError(
                        f"Cannot read into variable of type {arg.data_type.value}"
                    )

    def _get_function_return_type(self, tab_index: int) -> DataType:
        # Get return type dari function
        # Return type disimpan di entry.type untuk function
        
        entry = self.symbol_table.tab[tab_index]
        
        if entry.obj != ObjectType.FUNCTION:
            raise SemanticError(f"'{entry.id}' is not a function")
        
        return entry.type