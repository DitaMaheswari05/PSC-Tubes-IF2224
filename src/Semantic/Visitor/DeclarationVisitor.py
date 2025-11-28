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
        
        if not node or not hasattr(node, 'children'):
            return declarations
        
        # Iterasi semua children di declaration part
        for child in node.children:
            try:
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
            except Exception as e:
                raise SemanticError(f"Error in declaration processing: {str(e)}")
        
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
        
        if not node or not hasattr(node, 'children'):
            return var_decls
        
        # VarDeclarationNode structure: KEYWORD(variabel) (IdentifierListNode COLON TypeNode SEMICOLON)+
        i = 0
        children = node.children
        
        # Skip initial KEYWORD(variabel)
        while i < len(children):
            if isinstance(children[i], Token) and children[i].tokenType == TokenType.KEYWORD:
                if children[i].value.lower() in ["variabel", "var"]:
                    i += 1
                    break
            i += 1
        
        # Process each identifier-list/type pair
        while i < len(children):
            identifiers = []
            var_type = DataType.VOID
            var_ref = 0
            
            # Get identifiers from IdentifierListNode
            if i < len(children) and isinstance(children[i], IdentifierListNode):
                id_list_node = children[i]
                # Extract identifiers from IdentifierListNode
                for child in id_list_node.children:
                    if isinstance(child, Token) and child.tokenType == TokenType.IDENTIFIER:
                        identifiers.append(child.value)
                i += 1
            
            # Skip COLON
            if i < len(children) and isinstance(children[i], Token) and children[i].tokenType == TokenType.COLON:
                i += 1
            
            # Get type from TypeNode
            if i < len(children):
                child = children[i]
                
                # TypeNode
                if isinstance(child, TypeNode):
                    type_info = self._get_type_info(child)
                    var_type = type_info[0]
                    var_ref = type_info[1]
                    i += 1
                
                # Simple type keyword (fallback)
                elif isinstance(child, Token) and child.tokenType == TokenType.KEYWORD:
                    type_str = child.value.lower()
                    if type_str == "integer":
                        var_type = DataType.INTEGER
                    elif type_str == "real":
                        var_type = DataType.REAL
                    elif type_str == "boolean":
                        var_type = DataType.BOOLEAN
                    elif type_str == "char":
                        var_type = DataType.CHAR
                    elif type_str == "string":
                        var_type = DataType.STRING
                    i += 1
            
            # Skip semicolon
            if i < len(children) and isinstance(children[i], Token) and children[i].tokenType == TokenType.SEMICOLON:
                i += 1
            
            # Register each identifier in symbol table
            for identifier in identifiers:
                if identifier.lower() in ["integer", "real", "boolean", "char", "string", "larik", "dari"]:
                    # Skip type keywords that might appear in wrong position
                    continue
                
                # Check redeclaration in current block
                current_block = self.symbol_table.btab[self.symbol_table.display[self.symbol_table.level]]
                current_idx = current_block.last
                
                while current_idx != 0:
                    entry = self.symbol_table.tab[current_idx]
                    if entry.id.lower() == identifier.lower():
                        raise RedeclarationError(f"Identifier '{identifier}' already declared in current scope")
                    current_idx = entry.link
                
                # Enter identifier into symbol table
                tab_idx = self.symbol_table.enter_identifier(
                    identifier, 
                    ObjectType.VARIABLE, 
                    var_type, 
                    var_ref
                )
                
                # Create AST node dengan var_type argument
                var_ast = VarDeclASTNode(identifier, var_type)
                var_ast.annotate(data_type=var_type, tab_index=tab_idx, scope_level=self.symbol_table.level)
                var_decls.append(var_ast)
        
        return var_decls
    
    def visit_procedure_declaration(self, node: ProcedureDeclarationNode) -> ProcedureDeclASTNode:
        """Visit procedure declaration"""
        # Ambil nama prosedur dari IDENTIFIER
        proc_name = None
        
        for child in node.children:
            if isinstance(child, Token) and child.tokenType == TokenType.IDENTIFIER:
                proc_name = child.value
                break
        
        if not proc_name:
            raise SemanticError("Procedure name not found")
        
        # Check if already declared
        if self.symbol_table.lookup_identifier(proc_name) is not None:
            # Cek apakah di block yang sama
            current_block = self.symbol_table.btab[self.symbol_table.display[self.symbol_table.level]]
            current_idx = current_block.last
            
            while current_idx != 0:
                entry = self.symbol_table.tab[current_idx]
                if entry.id.lower() == proc_name.lower():
                    raise RedeclarationError(f"Procedure '{proc_name}' already declared in current scope")
                current_idx = entry.link
        
        # Register procedure in symbol table BEFORE entering new block
        # so it can be called from the parent scope
        tab_idx = self.symbol_table.enter_identifier(
            proc_name,
            ObjectType.PROCEDURE,
            DataType.VOID,
            0  # Temporary, will update with block_idx later
        )
        
        # Create new block for procedure
        block_idx = self.symbol_table.enter_block()
        
        # Update procedure entry with correct block_idx
        self.symbol_table.tab[tab_idx].ref = block_idx
        
        # Now process parameters, declarations, and compound statement IN ORDER within the new block
        param_list = None
        declarations = []
        compound_stmt = None
        
        for child in node.children:
            if isinstance(child, FormalParameterListNode):
                param_list = self.visit_formal_parameter_list(child)
            elif isinstance(child, DeclarationPartNode):
                declarations = self.visit_declaration_part(child)
            elif isinstance(child, CompoundStatementNode):

                
                from Semantic.Visitor.StatementVisitor import StatementVisitor
                stmt_visitor = StatementVisitor()
                stmt_visitor.symbol_table = self.symbol_table
                compound_stmt = stmt_visitor.visit_compound_statement(child)
        
        # Create AST node
        proc_ast = ProcedureDeclASTNode(proc_name)
        proc_ast.annotate(data_type=DataType.VOID, tab_index=tab_idx, block_index=block_idx, scope_level=self.symbol_table.level)
        
        # Exit block
        self.symbol_table.exit_block()
        
        return proc_ast
    
    def visit_function_declaration(self, node: FunctionDeclarationNode) -> FunctionDeclASTNode:
        """Visit function declaration"""
        # Ambil nama fungsi dari IDENTIFIER dan return type
        func_name = None
        return_type = DataType.VOID
        return_ref = 0
        param_list = None
        declarations = []
        compound_stmt = None
        
        for child in node.children:
            if isinstance(child, Token) and child.tokenType == TokenType.IDENTIFIER:
                func_name = child.value
            elif isinstance(child, Token) and child.tokenType == TokenType.KEYWORD:
                return_type = self.symbol_table.get_type_from_keyword(child.value)
            elif isinstance(child, TypeNode):
                type_info = self._get_type_info(child)
                return_type = type_info[0]
                return_ref = type_info[1]
            elif isinstance(child, FormalParameterListNode):
                param_list = self.visit_formal_parameter_list(child)
            elif isinstance(child, DeclarationPartNode):
                declarations = self.visit_declaration_part(child)
            elif isinstance(child, CompoundStatementNode):
                from Semantic.Visitor.StatementVisitor import StatementVisitor
                stmt_visitor = StatementVisitor()
                stmt_visitor.symbol_table = self.symbol_table
                compound_stmt = stmt_visitor.visit_compound_statement(child)
        
        if not func_name:
            raise SemanticError("Function name not found")
        
        # Check if already declared
        current_block = self.symbol_table.btab[self.symbol_table.display[self.symbol_table.level]]
        current_idx = current_block.last
        
        while current_idx != 0:
            entry = self.symbol_table.tab[current_idx]
            if entry.id.lower() == func_name.lower():
                raise RedeclarationError(f"Function '{func_name}' already declared in current scope")
            current_idx = entry.link
        
        # Create new block for function
        block_idx = self.symbol_table.enter_block()
        
        # Register function in symbol table
        tab_idx = self.symbol_table.enter_identifier(
            func_name,
            ObjectType.FUNCTION,
            return_type,
            return_ref
        )
        
        # Create AST node
        func_ast = FunctionDeclASTNode(func_name, return_type)
        func_ast.annotate(data_type=return_type, tab_index=tab_idx, block_index=block_idx, scope_level=self.symbol_table.level)
        
        # Exit block
        self.symbol_table.exit_block()
        
        return func_ast
    
    def visit_formal_parameter_list(self, node: FormalParameterListNode) -> List[VarDeclASTNode]:
        """Visit formal parameter list"""
        params = []
        

        
        # Process formal parameters similar to var declaration
        i = 0
        children = node.children
        

        
        # Skip LPAREN if present
        if i < len(children) and isinstance(children[i], Token) and children[i].tokenType == TokenType.LPARENTHESIS:
            i += 1
        
        while i < len(children):
            if isinstance(children[i], Token) and children[i].tokenType == TokenType.RPARENTHESIS:
                break
            
            identifiers = []
            param_type = DataType.VOID
            param_ref = 0
            nrm = 1  # by-value default
            
            # Check for var keyword (by-reference)
            if isinstance(children[i], Token) and children[i].tokenType == TokenType.KEYWORD and children[i].value == "variabel":
                nrm = 0
                i += 1
            
            # Collect parameter names from IdentifierListNode
            if i < len(children) and isinstance(children[i], IdentifierListNode):
                id_list_node = children[i]
                # Extract identifiers from IdentifierListNode 
                for child in id_list_node.children:
                    if isinstance(child, Token) and child.tokenType == TokenType.IDENTIFIER:
                        identifiers.append(child.value)
                i += 1
                
                # Skip COLON
                if i < len(children) and isinstance(children[i], Token) and children[i].tokenType == TokenType.COLON:
                    i += 1
            
            # Get parameter type
            if i < len(children):
                child = children[i]
                if isinstance(child, Token) and child.tokenType == TokenType.KEYWORD:
                    param_type = self.symbol_table.get_type_from_keyword(child.value)
                    i += 1
                elif isinstance(child, TypeNode):
                    # Extract type from TypeNode - look for KEYWORD inside
                    for type_child in child.children:
                        if isinstance(type_child, Token) and type_child.tokenType == TokenType.KEYWORD:
                            param_type = self.symbol_table.get_type_from_keyword(type_child.value)
                            break
                    i += 1
            
            # Skip semicolon or comma
            if i < len(children) and isinstance(children[i], Token):
                if children[i].tokenType == TokenType.SEMICOLON:
                    i += 1
                elif children[i].tokenType == TokenType.COMMA:
                    i += 1
            
            # Register each parameter

            for identifier in identifiers:
                tab_idx = self.symbol_table.enter_identifier(
                    identifier,
                    ObjectType.PARAMETER,
                    param_type,
                    param_ref,
                    nrm
                )
                
                # Set lpar to point to the last parameter for the current block
                current_block_index = self.symbol_table.display[self.symbol_table.level]
                current_block = self.symbol_table.btab[current_block_index]
                current_block.lpar = tab_idx
                
                param_ast = VarDeclASTNode(identifier, param_type)
                param_ast.annotate(data_type=param_type, tab_index=tab_idx, scope_level=self.symbol_table.level)
                params.append(param_ast)
        
        return params