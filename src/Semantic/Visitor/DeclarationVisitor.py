from typing import List
from Parser.ast import *
from src.Semantic.Visitor.SemanticAnalyzerBase import SemanticAnalyzerBase
from src.Semantic.Visitor.SemanticError import *
from src.Semantic.SymbolTable.SymbolTable import *
from src.Semantic.DecoratedAST.DecoratedASTNode import *
from src.Semantic.Visitor.StatementVisitor import StatementVisitor
from Repository.TokenType import TokenType
from Model.Token import Token

class DeclarationVisitor(SemanticAnalyzerBase):
    # Visitor untuk semantic analysis declaration nodes
    
    def visit_declaration_part(self, node: DeclarationPartNode) -> List[DecoratedASTNode]:
        # Visit declaration part
        
        declarations = []
        
        for child in node.children:
            if isinstance(child, ConstDeclarationNode):
                const_decls = self.visit_const_declaration(child)
                declarations.extend(const_decls)
            elif isinstance(child, TypeDeclarationNode):
                type_decls = self.visit_type_declaration(child)
                declarations.extend(type_decls)
            elif isinstance(child, VarDeclarationNode):
                var_decls = self.visit_var_declaration(child)
                declarations.extend(var_decls)
            elif isinstance(child, ProcedureDeclarationNode):
                proc_decl = self.visit_procedure_declaration(child)
                declarations.append(proc_decl)
            elif isinstance(child, FunctionDeclarationNode):
                func_decl = self.visit_function_declaration(child)
                declarations.append(func_decl)
        
        return declarations
    
    def visit_const_declaration(self, node: ConstDeclarationNode) -> List[ConstDeclASTNode]:
        # Visit constant declaration
        
        const_decls = []
        
        # Parse konstanta declarations
        i = 0
        while i < len(node.children):
            child = node.children[i]
            
            # Skip keyword 'konstanta'
            if isinstance(child, Token) and child.tokenType == TokenType.KEYWORD:
                i += 1
                continue
            
            # Cari identifier
            if isinstance(child, Token) and child.tokenType == TokenType.IDENTIFIER:
                const_name = child.value
                
                # Cek apakah identifier sudah dideklarasikan di scope ini
                current_block_index = self.symbol_table.display[self.symbol_table.level]
                current_block = self.symbol_table.btab[current_block_index]
                check_index = current_block.last
                while check_index != 0:
                    entry = self.symbol_table.tab[check_index]
                    if entry.identifier.lower() == const_name.lower():
                        raise RedeclarationError(const_name)
                    check_index = entry.link
                
                # Skip '=' token
                i += 1
                if i < len(node.children) and isinstance(node.children[i], Token):
                    i += 1
                
                # get constant value
                if i < len(node.children):
                    value_token = node.children[i]
                    value, const_type = self._get_constant_value(value_token)
                    
                    # enter constant ke symbol table
                    # adr menyimpan nilai konstanta
                    const_idx = self.symbol_table.enter_identifier(identifier=const_name, obj=ObjectType.CONSTANT, data_type=const_type, ref=0, nrm=1, adr=value)
                    
                    # Buat ast node
                    const_ast = ConstDeclASTNode(const_name, value, const_type)
                    const_ast.annotate(data_type=const_type, tab_index=const_idx, scope_level=self.symbol_table.level)
                    const_decls.append(const_ast)
                    
                    i += 1
            
            # Skip semicolon
            if i < len(node.children) and isinstance(node.children[i], Token) and node.children[i].tokenType == TokenType.SEMICOLON:
                i += 1
            else:
                i += 1
        
        return const_decls
    
    def visit_type_declaration(self, node: TypeDeclarationNode) -> List[TypeDeclASTNode]:
        # Visit type declaration
        
        type_decls = []
        
        i = 0
        while i < len(node.children):
            child = node.children[i]
            
            # Skip keyword 'tipe'
            if isinstance(child, Token) and child.tokenType == TokenType.KEYWORD:
                i += 1
                continue
            
            # Cari identifier untuk nama tipe
            if isinstance(child, Token) and child.tokenType == TokenType.IDENTIFIER:
                type_name = child.value
                
                # Cek redeclaration
                current_block_index = self.symbol_table.display[self.symbol_table.level]
                current_block = self.symbol_table.btab[current_block_index]
                check_index = current_block.last
                while check_index != 0:
                    entry = self.symbol_table.tab[check_index]
                    if entry.identifier.lower() == type_name.lower():
                        raise RedeclarationError(type_name)
                    check_index = entry.link
                
                # Skip '=' token
                i += 1
                if i < len(node.children) and isinstance(node.children[i], Token):
                    i += 1
                
                # Get type definition
                if i < len(node.children):
                    type_def_node = node.children[i]
                    
                    # Jika type_def_node adalah Token IDENTIFIER (reference ke tipe lain)
                    if isinstance(type_def_node, Token) and type_def_node.tokenType == TokenType.IDENTIFIER:
                        # Lookup tipe yang direferensi
                        type_idx = self.symbol_table.lookup_identifier(type_def_node.value)
                        if type_idx is None:
                            raise UndefinedIdentifierError(type_def_node.value)
                        
                        type_entry = self.symbol_table.tab[type_idx]
                        if type_entry.obj != ObjectType.TYPE:
                            raise SemanticError(f"'{type_def_node.value}' is not a type")
                        
                        data_type = type_entry.type
                        ref = type_entry.ref
                    else:
                        data_type, ref = self._get_type_info(type_def_node)
                    
                    # Enter type ke symbol table
                    type_idx = self.symbol_table.enter_identifier(identifier=type_name, obj=ObjectType.TYPE, data_type=data_type, ref=ref, nrm=1, adr=0)
                    
                    # Buat ast node
                    type_ast = TypeDeclASTNode(type_name, data_type)
                    type_ast.annotate(data_type=data_type, tab_index=type_idx, scope_level=self.symbol_table.level)
                    type_decls.append(type_ast)
                    
                    i += 1
            
            # Skip semicolon
            if i < len(node.children) and isinstance(node.children[i], Token) and node.children[i].tokenType == TokenType.SEMICOLON:
                i += 1
            else:
                i += 1
        
        return type_decls
    
    def visit_var_declaration(self, node: VarDeclarationNode) -> List[VarDeclASTNode]:
        # Visit variable declaration
        
        var_decls = []
        
        # Skip keyword 'variabel'
        identifiers = []
        var_type = DataType.VOID
        var_ref = 0
        
        for child in node.children:
            if isinstance(child, Token) and child.tokenType == TokenType.KEYWORD:
                continue
            elif isinstance(child, IdentifierListNode):
                identifiers = self._get_identifier_list(child)
            elif isinstance(child, TypeNode):
                var_type, var_ref = self._get_type_info(child)
        
        # Hitung ukuran untuk tipe ini
        var_size = self._get_size(var_type, var_ref)
        
        # Enter setiap identifier ke symbol table
        for identifier in identifiers:
            # Cek redeclaration
            current_block_index = self.symbol_table.display[self.symbol_table.level]
            current_block = self.symbol_table.btab[current_block_index]
            check_index = current_block.last
            while check_index != 0:
                entry = self.symbol_table.tab[check_index]
                if entry.identifier.lower() == identifier.lower():
                    raise RedeclarationError(identifier)
                check_index = entry.link
            
            # Get current block untuk menghitung address
            current_block = self.symbol_table.btab[self.symbol_table.display[self.symbol_table.level]]
            var_address = current_block.vsze
            
            # Enter variable ke symbol table
            var_idx = self.symbol_table.enter_identifier(
                identifier=identifier,
                obj=ObjectType.VARIABLE,
                data_type=var_type,
                ref=var_ref,
                nrm=1,  # Normal variable (not by-reference)
                adr=var_address
            )
            
            # Update block size
            current_block.vsze += var_size
            
            # Buat ast node
            var_ast = VarDeclASTNode(identifier, var_type)
            var_ast.annotate(
                data_type=var_type,
                tab_index=var_idx,
                scope_level=self.symbol_table.level
            )
            var_decls.append(var_ast)
        
        return var_decls

    
    def visit_procedure_declaration(self, node: ProcedureDeclarationNode) -> ProcedureDeclASTNode:
        # Visit procedure declaration (ada kaitan sama statement visitor)
        # Ambil nama procedure dan return type
        proc_name = None
        parameters = []
        declarations = []
        block = None
        
        for child in node.children:
            if isinstance(child, Token) and child.tokenType == TokenType.IDENTIFIER:
                proc_name = child.value
                break
        
        if proc_name is None:
            raise SemanticError("Procedure must have a name")
        
        # Cek redeclaration
        current_block_index = self.symbol_table.display[self.symbol_table.level]
        current_block = self.symbol_table.btab[current_block_index]
        check_index = current_block.last
        while check_index != 0:
            entry = self.symbol_table.tab[check_index]
            if entry.identifier.lower() == proc_name.lower():
                raise RedeclarationError(proc_name)
            check_index = entry.link
        
        # Enter procedure ke symbol table (di parent scope) dulu
        # Buat placeholder untuk ref yang bakal diisi setelah block dibuat
        proc_idx = self.symbol_table.enter_identifier(
            identifier=proc_name,
            obj=ObjectType.PROCEDURE,
            data_type=DataType.VOID,
            ref=0,  # Temporary, akan diupdate
            nrm=1,
            adr=0  # Address akan diisi saat code generation
        )
        
        proc_block_idx = self.symbol_table.enter_block() # Buat block entry untuk procedure
        self.symbol_table.tab[proc_idx].ref = proc_block_idx # Update ref di procedure entry untuk menunjuk ke block-nya
        
        # Parse children (sudah di dalam scope procedure karena enter_block menaikkan level)
        for child in node.children:
            if isinstance(child, FormalParameterListNode):
                parameters = self.visit_formal_parameter_list(child)
            elif isinstance(child, DeclarationPartNode):
                declarations = self.visit_declaration_part(child)
            elif isinstance(child, CompoundStatementNode):
                stmt_visitor = StatementVisitor()
                stmt_visitor.symbol_table = self.symbol_table
                stmt_visitor.errors = self.errors
                block = stmt_visitor.visit_compound_statement(child)
        
        # Update block entry
        proc_block = self.symbol_table.btab[proc_block_idx]
        if parameters:
            # lpar points to last parameter
            proc_block.lpar = parameters[-1].tab_index if parameters else 0
        
        # Simpan level saat ini sebelum exit
        proc_level = self.symbol_table.level - 1  # Level di mana procedure didefinisikan
        
        # Exit block (decrease level)
        self.symbol_table.exit_block()
        
        # Buat AST node
        proc_ast = ProcedureDeclASTNode(proc_name)
        proc_ast.parameters = parameters
        proc_ast.declarations = declarations
        proc_ast.block = block
        proc_ast.annotate(data_type=DataType.VOID, tab_index=proc_idx, block_index=proc_block_idx, scope_level=proc_level)
        
        return proc_ast
    
    def visit_function_declaration(self, node: FunctionDeclarationNode) -> FunctionDeclASTNode:
        # Visit function declaration (ada kaitan sama statement visitor)
        # Ambil nama fungsi dan return type
        func_name = None
        return_type = DataType.VOID
        return_ref = 0
        parameters = []
        declarations = []
        block = None
        
        i = 0
        while i < len(node.children):
            child = node.children[i]
            
            if isinstance(child, Token) and child.tokenType == TokenType.IDENTIFIER:
                func_name = child.value
                # Look ahead untuk return type (after colon ':)
                j = i + 1
                while j < len(node.children):
                    if isinstance(node.children[j], Token) and node.children[j].tokenType == TokenType.COLON:
                        if j + 1 < len(node.children):
                            type_node = node.children[j + 1]
                            if isinstance(type_node, TypeNode):
                                return_type, return_ref = self._get_type_info(type_node)
                            elif isinstance(type_node, Token) and type_node.tokenType == TokenType.KEYWORD:
                                return_type = self.symbol_table.get_type_from_keyword(type_node.value)
                        break
                    j += 1
                break
            i += 1
        
        if func_name is None:
            raise SemanticError("Function must have a name")
        
        # Cek redeclaration
        current_block_index = self.symbol_table.display[self.symbol_table.level]
        current_block = self.symbol_table.btab[current_block_index]
        check_index = current_block.last
        while check_index != 0:
            entry = self.symbol_table.tab[check_index]
            if entry.identifier.lower() == func_name.lower():
                raise RedeclarationError(func_name)
            check_index = entry.link
        
        # Enter function ke symbol table (di parent scope) dulu
        func_idx = self.symbol_table.enter_identifier(
            identifier=func_name,
            obj=ObjectType.FUNCTION,
            data_type=return_type,
            ref=0,  # Temporary, akan diupdate
            nrm=1,
            adr=0  # Address akan diisi saat code generation
        )
        
        func_block_idx = self.symbol_table.enter_block() # Buat block entry untuk function
        self.symbol_table.tab[func_idx].ref = func_block_idx # Update ref di function entry untuk menunjuk ke block-nya
        self.current_function_return_type = return_type # Set current function return type untuk validasi di statement visitor
        
        # Parse children (sudah di dalam scope function karena enter_block menaikkan level)
        for child in node.children:
            if isinstance(child, FormalParameterListNode):
                parameters = self.visit_formal_parameter_list(child)
            elif isinstance(child, DeclarationPartNode):
                declarations = self.visit_declaration_part(child)
            elif isinstance(child, CompoundStatementNode):
                stmt_visitor = StatementVisitor()
                stmt_visitor.symbol_table = self.symbol_table
                stmt_visitor.errors = self.errors
                stmt_visitor.current_function_return_type = return_type
                block = stmt_visitor.visit_compound_statement(child)
        
        # Update block entry
        func_block = self.symbol_table.btab[func_block_idx]
        if parameters:
            func_block.lpar = parameters[-1].tab_index if parameters else 0
        
        # Reset current function return type
        self.current_function_return_type = None
        
        # Simpan level saat ini sebelum exit
        func_level = self.symbol_table.level - 1  # Level di mana function didefinisikan
        
        # Exit block (decrease level)
        self.symbol_table.exit_block()
        
        # Buat ast node
        func_ast = FunctionDeclASTNode(func_name, return_type)
        func_ast.parameters = parameters
        func_ast.declarations = declarations
        func_ast.block = block
        func_ast.annotate(data_type=return_type, tab_index=func_idx, block_index=func_block_idx, scope_level=func_level)
        
        return func_ast
    
    def visit_formal_parameter_list(self, node: FormalParameterListNode) -> List[VarDeclASTNode]:
        # Visit formal parameter list
        parameters = []
        
        i = 0
        while i < len(node.children):
            child = node.children[i]
            
            # Skip parentheses dan semicolon
            if isinstance(child, Token) and child.tokenType in [TokenType.LPARENTHESIS, TokenType.RPARENTHESIS, TokenType.SEMICOLON, TokenType.COMMA]:
                i += 1
                continue
            
            # Cek 'var' keyword (by-reference parameter)
            is_var_param = False
            if isinstance(child, Token) and child.tokenType == TokenType.KEYWORD and child.value.lower() == 'var':
                is_var_param = True
                i += 1
                if i >= len(node.children):
                    break
                child = node.children[i]
            
            # Get identifier list
            identifiers = []
            param_type = DataType.VOID
            param_ref = 0
            
            if isinstance(child, IdentifierListNode):
                identifiers = self._get_identifier_list(child)
                
                # Cari colon dan type
                j = i + 1
                while j < len(node.children):
                    if isinstance(node.children[j], Token) and node.children[j].tokenType == TokenType.COLON:
                        if j + 1 < len(node.children):
                            type_node = node.children[j + 1]
                            if isinstance(type_node, TypeNode):
                                param_type, param_ref = self._get_type_info(type_node)
                            elif isinstance(type_node, Token) and type_node.tokenType == TokenType.KEYWORD:
                                param_type = self.symbol_table.get_type_from_keyword(type_node.value)
                            elif isinstance(type_node, Token) and type_node.tokenType == TokenType.IDENTIFIER:
                                type_idx = self.symbol_table.lookup_identifier(type_node.value)
                                if type_idx:
                                    type_entry = self.symbol_table.tab[type_idx]
                                    if type_entry.obj == ObjectType.TYPE:
                                        param_type = type_entry.type
                                        param_ref = type_entry.ref
                        break
                    j += 1
                
                # Enter parameters ke symbol table
                param_size = self._get_size(param_type, param_ref)
                current_block = self.symbol_table.btab[self.symbol_table.display[self.symbol_table.level]]
                
                for identifier in identifiers:
                    # Parameter disimpan dengan psze (parameter size)
                    param_address = current_block.psze
                    
                    # Enter parameter
                    param_idx = self.symbol_table.enter_identifier(
                        identifier=identifier,
                        obj=ObjectType.VARIABLE,
                        data_type=param_type,
                        ref=param_ref,
                        nrm=0 if is_var_param else 1,  # nrm=0 untuk var parameter (by-reference)
                        adr=param_address
                    )
                    
                    # Update parameter size
                    current_block.psze += param_size
                    
                    # Buat ast node
                    param_ast = VarDeclASTNode(identifier, param_type)
                    param_ast.annotate(data_type=param_type, tab_index=param_idx, scope_level=self.symbol_table.level)
                    parameters.append(param_ast)
            
            i += 1
        
        return parameters