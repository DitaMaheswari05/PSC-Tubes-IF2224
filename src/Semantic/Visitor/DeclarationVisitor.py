from typing import List
from Parser.ast import *
from Semantic.Visitor.SemanticAnalyzerBase import SemanticAnalyzerBase
from Semantic.Visitor.SemanticError import *
from Semantic.SymbolTable.SymbolTable import *
from Semantic.DecoratedAST.DecoratedASTNode import *
from Semantic.Visitor.StatementVisitor import StatementVisitor
from Repository.TokenType import TokenType
from Model.Token import Token

# ini template aja, atur-atur sesuai kebutuhan
class DeclarationVisitor(SemanticAnalyzerBase):
    """Visitor untuk semantic analysis declaration nodes"""
    
    def visit_declaration_part(self, node: DeclarationPartNode) -> List[DecoratedASTNode]:
        """Visit declaration part dan return list of declaration AST nodes"""
        declarations = []
        
        # Iterasi semua children di declaration part
        for child in node.children:
            # Const declaration
            if isinstance(child, ConstDeclarationNode):
                const_decls = self.visit_const_declaration(child)
                if const_decls:
                    declarations.extend(const_decls)
            
            # Type declaration
            elif isinstance(child, TypeDeclarationNode):
                type_decls = self.visit_type_declaration(child)
                if type_decls:
                    declarations.extend(type_decls)
            
            # Var declaration
            elif isinstance(child, VarDeclarationNode):
                var_decls = self.visit_var_declaration(child)
                if var_decls:
                    declarations.extend(var_decls)
            
            # Procedure declaration
            elif isinstance(child, ProcedureDeclarationNode):
                proc_decl = self.visit_procedure_declaration(child)
                if proc_decl:
                    declarations.append(proc_decl)
            
            # Function declaration
            elif isinstance(child, FunctionDeclarationNode):
                func_decl = self.visit_function_declaration(child)
                if func_decl:
                    declarations.append(func_decl)
        
        return declarations
    
    def visit_const_declaration(self, node: ConstDeclarationNode) -> List[ConstDeclASTNode]:
        """Visit constant declaration"""
        # TODO: Implementasi nanti jika diperlukan
        return []
    
    def visit_type_declaration(self, node: TypeDeclarationNode) -> List[TypeDeclASTNode]:
        """Visit type declaration"""
        # TODO: Implementasi nanti jika diperlukan
        return []
    
    def visit_var_declaration(self, node: VarDeclarationNode) -> List[VarDeclASTNode]:
        """Visit variable declaration"""
        var_decls = []
        
        # Process identifier lists and types in sequence
        # VarDeclarationNode structure: KEYWORD(variabel) (identifier-list COLON type SEMICOLON)+
        i = 0
        children = node.children
        
        # Skip initial KEYWORD(variabel)
        if i < len(children) and isinstance(children[i], Token) and children[i].tokenType == TokenType.KEYWORD:
            i += 1
        
        # Process each identifier-list/type pair
        while i < len(children):
            identifiers = []
            var_type = DataType.VOID
            var_ref = 0
            
            # Get identifier list
            if i < len(children) and isinstance(children[i], IdentifierListNode):
                identifiers = self._get_identifier_list(children[i])
                i += 1
            else:
                break
            
            # Skip COLON token
            if i < len(children) and isinstance(children[i], Token) and children[i].tokenType == TokenType.COLON:
                i += 1
            
            # Get type
            if i < len(children) and isinstance(children[i], TypeNode):
                var_type, var_ref = self._get_type_info(children[i])
                i += 1
            
            # Skip SEMICOLON token
            if i < len(children) and isinstance(children[i], Token) and children[i].tokenType == TokenType.SEMICOLON:
                i += 1
            
            # Hitung ukuran variable
            var_size = self._get_size(var_type, var_ref)
            
            # Masukkan setiap identifier ke symbol table
            for identifier in identifiers:
                # Cek apakah sudah dideklarasikan di scope saat ini
                current_block_idx = self.symbol_table.display[self.symbol_table.level]
                current_block = self.symbol_table.btab[current_block_idx]
                
                # Cari di linked list block saat ini
                idx = current_block.last
                while idx != 0:
                    entry = self.symbol_table.tab[idx]
                    if entry.id.lower() == identifier.lower():
                        raise RedeclarationError(identifier)
                    idx = entry.link
                
                # Masukkan ke symbol table
                tab_idx = self.symbol_table.enter_identifier(
                    identifier=identifier,
                    obj=ObjectType.VARIABLE,
                    data_type=var_type,
                    ref=var_ref,
                    nrm=1,  # Normal variable (bukan by-reference)
                    adr=current_block.vsze  # Address = current variable size
                )
                
                # Update variable size di block
                current_block.vsze += var_size
                
                # Buat VarDeclASTNode
                var_ast = VarDeclASTNode(identifier, var_type)
                var_ast.annotate(
                    data_type=var_type,
                    tab_index=tab_idx,
                    scope_level=self.symbol_table.level
                )
                var_decls.append(var_ast)
        
        return var_decls
    
    def visit_procedure_declaration(self, node: ProcedureDeclarationNode) -> ProcedureDeclASTNode:
        """Visit prosedur declaration dan proses body nya"""
        proc_name = None
        parameters = []
        
        # Extract procedure name dan parameter list dari children
        for child in node.children:
            # Get procedure name dari IDENTIFIER token
            if isinstance(child, Token) and child.tokenType == TokenType.IDENTIFIER:
                proc_name = child.value
            # Get parameter list jika ada
            elif isinstance(child, FormalParameterListNode):
                parameters = self.visit_formal_parameter_list(child)
        
        if not proc_name:
            raise SyntaxError("Procedure name tidak ditemukan")
        
        # Hitung total parameter size
        total_param_size = sum(self._get_size(p.data_type, 0) for p in parameters)
        
        # Cek redeclaration di scope saat ini (sama seperti var declaration)
        current_block_idx = self.symbol_table.display[self.symbol_table.level]
        current_block = self.symbol_table.btab[current_block_idx]
        idx = current_block.last
        while idx != 0:
            entry = self.symbol_table.tab[idx]
            if entry.id.lower() == proc_name.lower():
                raise RedeclarationError(proc_name)
            idx = entry.link
        
        # Masukkan procedure ke symbol table (ref = index block baru untuk prosedur)
        block_idx = len(self.symbol_table.btab)
        tab_idx = self.symbol_table.enter_identifier(
            identifier=proc_name,
            obj=ObjectType.PROCEDURE,
            data_type=DataType.VOID,  # Procedure tidak return tipe
            ref=block_idx,  # Refer ke block table
            nrm=1,
            adr=0
        )
        
        # Buat block baru untuk procedure
        new_block = BTabEntry(
            last=0,
            lpar=0,
            psze=total_param_size,
            vsze=0
        )
        self.symbol_table.btab.append(new_block)
        
        # Naik ke level lebih dalam (masuk block prosedur)
        self.symbol_table.level += 1
        self.symbol_table.display.append(block_idx)
        
        # Masukkan parameters ke symbol table SETELAH naik level
        first_param_idx = len(self.symbol_table.tab)
        for param in parameters:
            self.symbol_table.enter_identifier(
                identifier=param.identifier,
                obj=ObjectType.PARAMETER,
                data_type=param.data_type,
                ref=0,
                nrm=0,  # By-reference parameter (var parameter)
                adr=0
            )
        
        # Update last parameter pointer untuk block procedure
        if parameters:
            self.symbol_table.btab[block_idx].lpar = len(self.symbol_table.tab) - 1
            self.symbol_table.btab[block_idx].last = len(self.symbol_table.tab) - 1
        
        # Visit body prosedur
        body_ast = None
        for child in node.children:
            if isinstance(child, CompoundStatementNode):
                from Semantic.Visitor.StatementVisitor import StatementVisitor
                statement_visitor = StatementVisitor()
                statement_visitor.symbol_table = self.symbol_table
                body_ast = statement_visitor.visit_compound_statement(child)
                break
        
        # Turun kembali ke level sebelumnya
        self.symbol_table.level -= 1
        self.symbol_table.display.pop()
        
        # Buat ProcedureDeclASTNode
        proc_ast = ProcedureDeclASTNode(proc_name)
        proc_ast.annotate(
            data_type=DataType.VOID,
            tab_index=tab_idx,
            scope_level=self.symbol_table.level
        )
        
        return proc_ast
    
    def visit_function_declaration(self, node: FunctionDeclarationNode) -> FunctionDeclASTNode:
        """Visit function declaration dan proses body nya"""
        func_name = None
        func_return_type = DataType.VOID
        parameters = []
        
        # Extract function name, return type, dan parameter list
        for child in node.children:
            # Get function name dari IDENTIFIER token
            if isinstance(child, Token) and child.tokenType == TokenType.IDENTIFIER:
                func_name = child.value
            # Get return type dari TypeNode
            elif isinstance(child, TypeNode):
                func_return_type, _ = self._get_type_info(child)
            # Get parameter list jika ada
            elif isinstance(child, FormalParameterListNode):
                parameters = self.visit_formal_parameter_list(child)
        
        if not func_name:
            raise SyntaxError("Function name tidak ditemukan")
        
        # Hitung total parameter size
        total_param_size = sum(self._get_size(p.data_type, 0) for p in parameters)
        
        # Cek redeclaration di scope saat ini
        current_block_idx = self.symbol_table.display[self.symbol_table.level]
        current_block = self.symbol_table.btab[current_block_idx]
        idx = current_block.last
        while idx != 0:
            entry = self.symbol_table.tab[idx]
            if entry.id.lower() == func_name.lower():
                raise RedeclarationError(func_name)
            idx = entry.link
        
        # Masukkan function ke symbol table
        block_idx = len(self.symbol_table.btab)
        tab_idx = self.symbol_table.enter_identifier(
            identifier=func_name,
            obj=ObjectType.FUNCTION,
            data_type=func_return_type,  # Function punya return type
            ref=block_idx,  # Refer ke block table
            nrm=1,
            adr=0
        )
        
        # Buat block baru untuk function
        new_block = BTabEntry(
            last=0,
            lpar=0,
            psze=total_param_size,
            vsze=0
        )
        self.symbol_table.btab.append(new_block)
        
        # Naik ke level lebih dalam
        self.symbol_table.level += 1
        self.symbol_table.display.append(block_idx)
        
        # Masukkan parameters SETELAH naik level
        first_param_idx = len(self.symbol_table.tab)
        for param in parameters:
            self.symbol_table.enter_identifier(
                identifier=param.identifier,
                obj=ObjectType.PARAMETER,
                data_type=param.data_type,
                ref=0,
                nrm=0,
                adr=0
            )
        
        # Update last parameter pointer
        if parameters:
            self.symbol_table.btab[block_idx].lpar = len(self.symbol_table.tab) - 1
            self.symbol_table.btab[block_idx].last = len(self.symbol_table.tab) - 1
        
        # Visit body function
        body_ast = None
        for child in node.children:
            if isinstance(child, CompoundStatementNode):
                from Semantic.Visitor.StatementVisitor import StatementVisitor
                statement_visitor = StatementVisitor()
                statement_visitor.symbol_table = self.symbol_table
                body_ast = statement_visitor.visit_compound_statement(child)
                break
        
        # Turun kembali
        self.symbol_table.level -= 1
        self.symbol_table.display.pop()
        
        # Buat FunctionDeclASTNode
        func_ast = FunctionDeclASTNode(func_name, func_return_type)
        func_ast.annotate(
            data_type=func_return_type,
            tab_index=tab_idx,
            scope_level=self.symbol_table.level
        )
        
        return func_ast
    
    def visit_formal_parameter_list(self, node: FormalParameterListNode) -> List[VarDeclASTNode]:
        """Visit formal parameter list dan extract parameters"""
        parameters = []
        
        # FormalParameterListNode structure:
        # LPAREN + IdentifierList + COLON + Type + RPAREN (simple case)
        # atau multiple parameter groups: (id1, id2: type1; id3: type2)
        
        identifiers = []
        param_type = DataType.VOID
        
        # Parse structure: LPAREN (token) -> IdentifierList -> COLON (token) -> Type -> optional more params
        for child in node.children:
            if isinstance(child, IdentifierListNode):
                # Extract identifiers
                identifiers = self._get_identifier_list(child)
            elif isinstance(child, TypeNode):
                # Extract type
                param_type, _ = self._get_type_info(child)
                
                # Buat parameter nodes untuk identifiers yang baru ditemukan
                for identifier in identifiers:
                    param_ast = VarDeclASTNode(identifier, param_type)
                    param_ast.data_type = param_type
                    param_ast.identifier = identifier
                    parameters.append(param_ast)
                
                # Reset untuk parameter group berikutnya (jika ada)
                identifiers = []
                param_type = DataType.VOID
        
        return parameters