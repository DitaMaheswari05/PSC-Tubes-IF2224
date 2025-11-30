from typing import List, Optional
from Parser.ast import *
from Semantic.Visitor.SemanticAnalyzerBase import SemanticAnalyzerBase
from Semantic.Visitor.SemanticError import *
from Semantic.SymbolTable.SymbolTable import *
from Semantic.DecoratedAST.DecoratedASTNode import *
from Repository.TokenType import TokenType
from Model.Token import Token

class ProcFuncVisitor(SemanticAnalyzerBase):
    # visitor untuk semantic analysis procedure dan function call
    
    def visit_procedure_call(self, node: CallStatementNode) -> ProcCallASTNode:
        # visit procedure call statement
        # struktur node: identifier/keyword lparenthesis [parameterlistnode] rparenthesis
        
        children = node.children
        if not children:
            raise SemanticError("Empty procedure call node")
        
        # ambil nama procedure (bisa identifier atau keyword)
        name_token = children[0]
        if isinstance(name_token, Token):
            proc_name = name_token.value
            line = name_token.line
            column = name_token.column
        else:
            raise SemanticError("Expected procedure name")
        
        # parse arguments jika ada
        args: List[DecoratedASTNode] = []
        for child in children:
            if isinstance(child, ParameterListNode):
                # parse setiap argument dalam parameter list
                from Semantic.Visitor.ExpressionVisitor import ExpressionVisitor
                expr_visitor = ExpressionVisitor()
                expr_visitor.symbol_table = self.symbol_table
                expr_visitor.errors = self.errors
                
                for param_child in child.children:
                    # skip comma tokens
                    if isinstance(param_child, Token) and param_child.tokenType == TokenType.COMMA:
                        continue
                    
                    # parse expression untuk setiap parameter
                    if isinstance(param_child, ExpressionNode):
                        arg_ast = expr_visitor.visit_expression(param_child)
                        args.append(arg_ast)
        
        idx = self.symbol_table.lookup_identifier(proc_name)
        
        if idx is None:
            raise UndefinedIdentifierError(proc_name, line, column)
        
        entry = self.symbol_table.tab[idx]
        
        # validasi bahwa ini adalah procedure
        if entry.obj != ObjectType.PROCEDURE:
            raise TypeMismatchError(
                expected="PROCEDURE",
                got=entry.obj.value,
                context=f"'{proc_name}'",
                line=line,
                column=column
            )
        
        # Cek apakah built-in
        is_builtin = self.symbol_table.is_builtin_procedure(proc_name)
        
        if is_builtin:
            # Validasi khusus untuk built-in
            self._check_builtin_procedure(proc_name, args, line, column)
        else:
            # Validasi untuk user-defined
            self._validate_call_arguments(proc_name, idx, args, line, column)
        
        # Buat AST node dengan tab_index yang valid
        ast_node = ProcCallASTNode(proc_name, args)
        ast_node.annotate(
            data_type=DataType.VOID,
            tab_index=idx,
            scope_level=entry.lev
        )
        
        return ast_node
    
    def visit_function_call(self, node: CallStatementNode) -> FuncCallASTNode:
        # visit function call (dipanggil dari dalam expression)
        # struktur sama dengan procedure call tapi return type nya bukan void
        
        children = node.children
        if not children:
            raise SemanticError("Empty function call node")
        
        # ambil nama function
        name_token = children[0]
        if isinstance(name_token, Token):
            func_name = name_token.value
            line = name_token.line
            column = name_token.column
        else:
            raise SemanticError("Expected function name")
        
        # parse arguments
        args: List[DecoratedASTNode] = []
        for child in children:
            if isinstance(child, ParameterListNode):
                from Semantic.Visitor.ExpressionVisitor import ExpressionVisitor
                expr_visitor = ExpressionVisitor()
                expr_visitor.symbol_table = self.symbol_table
                expr_visitor.errors = self.errors
                
                for param_child in child.children:
                    if isinstance(param_child, Token) and param_child.tokenType == TokenType.COMMA:
                        continue
                    
                    if isinstance(param_child, ExpressionNode):
                        arg_ast = expr_visitor.visit_expression(param_child)
                        args.append(arg_ast)
        
        # lookup function
        idx = self.symbol_table.lookup_identifier(func_name)
        if idx is None:
            raise UndefinedIdentifierError(func_name, line, column)
        
        entry = self.symbol_table.tab[idx]
        
        # validasi bahwa ini adalah function
        if entry.obj != ObjectType.FUNCTION:
            raise TypeMismatchError(
                expected="FUNCTION",
                got=entry.obj.value,
                context=f"'{func_name}'",
                line=line,
                column=column
            )
        
        # validasi arguments
        self._validate_call_arguments(func_name, idx, args, line, column)
        
        # get return type
        return_type = self._get_function_return_type(idx)
        
        # buat funccallastnode
        ast_node = FuncCallASTNode(func_name, args)
        ast_node.annotate(
            data_type=return_type,
            tab_index=idx,
            scope_level=entry.lev
        )
        
        return ast_node

    def _validate_call_arguments(self, name: str, tab_index: int, args: List[DecoratedASTNode], 
                                 line: int = 0, column: int = 0):
        # validasi arguments untuk procedure/function call:
        # - jumlah argumen sesuai
        # - tipe argumen kompatibel dengan parameter
        # - by-reference parameter (var) hanya menerima lvalue
        
        # ambil parameter list
        params = self._get_parameter_list(tab_index)
        
        # cek jumlah parameter
        if len(args) != len(params):
            raise ParameterError(name, len(params), len(args), line, column)
        
        # validasi setiap argument dengan parameter
        for i, (param_name, param_type, is_var_param) in enumerate(params):
            arg = args[i]
            
            # cek tipe compatibility
            if arg.data_type != param_type:
                # allow implicit conversion integer → real
                if param_type == DataType.REAL and arg.data_type == DataType.INTEGER:
                    pass
                else:
                    raise TypeMismatchError(
                        expected=param_type.value,
                        got=arg.data_type.value,
                        context=f"parameter {i+1} of '{name}'",
                        line=line,
                        column=column
                    )
            
            # jika var parameter, harus lvalue (variable)
            if is_var_param:
                # cek apakah arg adalah lvalue (varastnode, arrayaccessastnode, recordaccessastnode)
                if not isinstance(arg, (VarASTNode, ArrayAccessASTNode, RecordAccessASTNode)):
                    raise InvalidAssignmentError(
                        target=f"parameter {i+1} of '{name}'",
                        reason="var parameter requires lvalue (variable)",
                        line=line,
                        column=column
                    )

    def _get_parameter_list(self, tab_index: int) -> List[tuple]:
        # ambil list parameter dari procedure/function
        # return: [(param_name, param_type, is_var_param), ...]
        
        entry = self.symbol_table.tab[tab_index]
        
        # ref menunjuk ke block entry untuk procedure/function
        if entry.ref <= 0 or entry.ref >= len(self.symbol_table.btab):
            return []  # tidak ada parameter
        
        block_entry = self.symbol_table.btab[entry.ref]
        
        # lpar menunjuk ke parameter terakhir dalam linked list
        # traverse dari lpar untuk mengumpulkan semua parameter
        params = []
        current_idx = block_entry.lpar
        
        # kumpulkan parameter dalam reverse order (karena linked list)
        param_indices = []
        while current_idx != 0:
            param_indices.append(current_idx)
            param_entry = self.symbol_table.tab[current_idx]
            current_idx = param_entry.link
        
        # balik urutan agar sesuai deklarasi
        param_indices.reverse()
        
        # buat list parameter
        for idx in param_indices:
            param_entry = self.symbol_table.tab[idx]
            if param_entry.obj == ObjectType.PARAMETER:
                # nrm=0 berarti var parameter (by reference)
                # nrm=1 berarti value parameter
                is_var_param = (param_entry.nrm == 0)
                params.append((param_entry.id, param_entry.type, is_var_param))
        
        return params

    def _check_builtin_procedure(self, name: str, args: List[DecoratedASTNode], 
                                 line: int = 0, column: int = 0):
        # validasi built-in procedures: writeln, write, readln, read
        # writeln/write: variadic, accept any type
        # readln/read: hanya variable (lvalue), dan harus tipe yang bisa dibaca
        
        name_lower = name.lower()
        
        if name_lower in ['writeln', 'write']:
            # writeln/write: accept any type
            pass
        
        elif name_lower in ['readln', 'read']:
            # readln/read: harus lvalue dan tipe yang bisa dibaca
            if len(args) == 0:
                # readln() tanpa parameter ok
                pass
            else:
                for i, arg in enumerate(args):
                    # cek apakah lvalue
                    if not isinstance(arg, (VarASTNode, ArrayAccessASTNode, RecordAccessASTNode)):
                        raise InvalidAssignmentError(
                            target=f"argument {i+1} of '{name}'",
                            reason="must be a variable (lvalue)",
                            line=line,
                            column=column
                        )
                    
                    # cek tipe yang bisa dibaca
                    readable_types = [DataType.INTEGER, DataType.REAL, DataType.CHAR, DataType.STRING]
                    if arg.data_type not in readable_types:
                        raise InvalidOperationError(
                            operation=f"read into {arg.data_type.value}",
                            operand_types=arg.data_type.value,
                            line=line,
                            column=column
                        )

    def _get_function_return_type(self, tab_index: int) -> DataType:
        # ambil return type dari function
        # return type disimpan di entry.type untuk function
        
        entry = self.symbol_table.tab[tab_index]
        
        if entry.obj != ObjectType.FUNCTION:
            raise SemanticError(f"'{entry.id}' is not a function")
        
        return entry.type
