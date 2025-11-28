from typing import List
from Parser.ast import *
from Semantic.Visitor.SemanticAnalyzerBase import SemanticAnalyzerBase
from Semantic.Visitor.SemanticError import *
from Semantic.SymbolTable.SymbolTable import SymbolTable
from Semantic.DecoratedAST.DecoratedASTNode import *
from Semantic.Visitor.ExpressionVisitor import ExpressionVisitor
from Semantic.Visitor.ProcFuncVisitor import ProcFuncVisitor
from Repository.TokenType import TokenType
from Model.Token import Token

class StatementVisitor(SemanticAnalyzerBase):
    # dispatcher untuk statement
    def visit_statement(self, node: ASTNode) -> Optional[DecoratedASTNode]:
        # Mengecek tipe node dan memanggil fungsi visit yang sesuai.
        if isinstance(node, CompoundStatementNode):
            return self.visit_compound_statement(node)
        
        elif isinstance(node, StatementListNode):
            return self.visit_statement_list(node)
            
        elif isinstance(node, AssignmentStatementNode):
            return self.visit_assignment_statement(node)
        
        elif isinstance(node, IfStatementNode):
            return self.visit_if_statement(node)
        
        elif isinstance(node, WhileStatementNode):
            return self.visit_while_statement(node)
        
        elif isinstance(node, RepeatStatementNode):
            return self.visit_repeat_statement(node)
        
        elif isinstance(node, ForStatementNode):
            return self.visit_for_statement(node)
            
        elif isinstance(node, CallStatementNode):
            return self.visit_call_statement(node)
            
        elif isinstance(node, CaseStatementNode):
            # Implementasi opsional jika CaseStatementNode digunakan
            pass 
            
        return None

    def visit_compound_statement(self, node: CompoundStatementNode) -> BlockASTNode:
        # compound-statement -> begin statement-list end
        
        # Cari child yang merupakan StatementListNode
        stmt_list_node = None
        for child in node.children:
            if isinstance(child, StatementListNode):
                stmt_list_node = child
                break
        
        # Jika ketemu, delegasikan ke visit_statement_list
        if stmt_list_node:
            return self.visit_statement_list(stmt_list_node)
        
        # Jika kosong (begin end)
        return BlockASTNode()

    def visit_statement_list(self, node: StatementListNode) -> BlockASTNode:
        # statement-list -> statement (semicolon statement)*
        
        block_node = BlockASTNode()
        
        for child in node.children:
            # Skip token SEMICOLON, hanya proses Node
            if isinstance(child, Token):
                continue
            
            # Panggil dispatcher untuk setiap statement
            stmt_result = self.visit_statement(child)
            if stmt_result:
                # Jika hasil visit adalah BlockASTNode (nested compound),
                # kita bisa flatten atau append langsung tergantung desain.
                # Di sini append sebagai satu kesatuan statement.
                block_node.statements.append(stmt_result)
                
        return block_node

    def visit_assignment_statement(self, node: AssignmentStatementNode) -> AssignASTNode:
        # assignment-statement -> variable := expression
        # Also handles: array_element := expression, record_field := expression
        
        target_token = None
        expression_node = None
        has_array_access = False
        has_field_access = False
        
        # Ekstrak anak secara manual
        for child in node.children:
            if isinstance(child, Token) and child.tokenType == TokenType.IDENTIFIER:
                target_token = child
            elif isinstance(child, Token) and child.tokenType == TokenType.LBRACKET:
                has_array_access = True
            elif isinstance(child, Token) and child.tokenType == TokenType.DOT:
                has_field_access = True
            elif isinstance(child, ExpressionNode):
                expression_node = child
                
        if not target_token or not expression_node:
            raise SemanticError("Malformed assignment statement")

        # 1. Lookup Variable/Array/Record
        idx = self.symbol_table.lookup_identifier(target_token.value)
        if idx is None:
            raise SemanticError(f"Undeclared variable '{target_token.value}'")
            
        entry = self.symbol_table.tab[idx]
        
        if entry.obj not in [ObjectType.VARIABLE, ObjectType.FUNCTION]:
             raise SemanticError(f"Cannot assign to '{target_token.value}' because it is a {entry.obj.name}")

        target_ast = VarASTNode(target_token.value)
        
        # Determine target type based on access type
        target_type = entry.type
        if has_array_access and entry.type == DataType.ARRAY:
            # Get array element type from atab
            array_ref = entry.ref
            if array_ref < len(self.symbol_table.atab):
                array_entry = self.symbol_table.atab[array_ref]
                target_type = array_entry.etyp  # Element type
        
        target_ast.annotate(data_type=target_type, tab_index=idx, scope_level=entry.lev)

        # 2. Visit Expression
        expr_visitor = self._get_expression_visitor()
        value_ast = expr_visitor.visit_expression(expression_node)
        
        if value_ast.data_type is None:
             value_ast.data_type = expr_visitor._infer_expression_type(value_ast)

        # 3. Type Checking
        if target_type != value_ast.data_type:
            if target_type == DataType.REAL and value_ast.data_type == DataType.INTEGER:
                pass 
            else:
                raise TypeMismatchError(target_type.name, value_ast.data_type.name, f"assignment to '{target_token.value}'")

        return AssignASTNode(target_ast, value_ast)

    def visit_if_statement(self, node: IfStatementNode) -> IfASTNode:
        # if-statement
        
        condition_node = None
        then_stmt_node = None
        else_stmt_node = None
        
        iterator = iter(node.children)
        try:
            for child in iterator:
                if isinstance(child, ExpressionNode):
                    condition_node = child
                elif isinstance(child, Token) and child.tokenType == TokenType.KEYWORD:
                    if child.value == 'maka': # 'then'
                        then_stmt_node = next(iterator)
                    elif child.value == 'selain-itu': # 'else'
                        else_stmt_node = next(iterator)
        except StopIteration:
            pass
            
        # 1. Validasi Kondisi
        expr_visitor = self._get_expression_visitor()
        cond_ast = expr_visitor.visit_expression(condition_node)
        
        if cond_ast.data_type is None:
             cond_ast.data_type = expr_visitor._infer_expression_type(cond_ast)
             
        if cond_ast.data_type != DataType.BOOLEAN:
            raise TypeMismatchError("BOOLEAN", cond_ast.data_type.name, "IF condition")

        # 2. Visit Statements
        then_ast = self.visit_statement(then_stmt_node)
        else_ast = self.visit_statement(else_stmt_node) if else_stmt_node else None
        
        return IfASTNode(cond_ast, then_ast, else_ast)

    def visit_while_statement(self, node: WhileStatementNode) -> WhileASTNode:
        # while-statement
        
        condition_node = None
        body_node = None
        
        for child in node.children:
            if isinstance(child, ExpressionNode):
                condition_node = child
            elif not isinstance(child, Token): 
                # Asumsi selain token adalah statement body
                body_node = child

        # 1. Validasi Kondisi
        expr_visitor = self._get_expression_visitor()
        cond_ast = expr_visitor.visit_expression(condition_node)
        
        if cond_ast.data_type is None:
             cond_ast.data_type = expr_visitor._infer_expression_type(cond_ast)

        if cond_ast.data_type != DataType.BOOLEAN:
            raise TypeMismatchError("BOOLEAN", cond_ast.data_type.name, "WHILE condition")

        # 2. Visit Body
        body_ast = self.visit_statement(body_node)
        
        return WhileASTNode(cond_ast, body_ast)

    def visit_for_statement(self, node: ForStatementNode) -> ForASTNode:
        # for-statement
        
        var_token = None
        start_expr = None
        end_expr = None
        body_node = None
        is_downto = False
        
        children = node.children
        for i, child in enumerate(children):
            if isinstance(child, Token):
                if child.tokenType == TokenType.IDENTIFIER:
                    var_token = child
                elif child.value == 'turun-ke':
                    is_downto = True
            elif isinstance(child, ExpressionNode):
                if start_expr is None:
                    start_expr = child
                else:
                    end_expr = child
            elif i == len(children) - 1: # Asumsi statement terakhir
                body_node = child

        # 1. Validasi Loop Variable
        idx = self.symbol_table.lookup_identifier(var_token.value)
        if idx is None:
            raise SemanticError(f"Undeclared loop variable '{var_token.value}'")
        
        entry = self.symbol_table.tab[idx]
        if entry.type != DataType.INTEGER:
             raise TypeMismatchError("INTEGER", entry.type.name, "FOR loop variable")

        # 2. Validasi Start & End
        expr_visitor = self._get_expression_visitor()
        
        start_ast = expr_visitor.visit_expression(start_expr)
        if start_ast.data_type is None: start_ast.data_type = expr_visitor._infer_expression_type(start_ast)
        
        end_ast = expr_visitor.visit_expression(end_expr)
        if end_ast.data_type is None: end_ast.data_type = expr_visitor._infer_expression_type(end_ast)
        
        if start_ast.data_type != DataType.INTEGER:
            raise TypeMismatchError("INTEGER", start_ast.data_type.name, "FOR start value")
            
        if end_ast.data_type != DataType.INTEGER:
            raise TypeMismatchError("INTEGER", end_ast.data_type.name, "FOR end value")

        # 3. Visit Body
        body_ast = self.visit_statement(body_node)
        
        return ForASTNode(var_token.value, start_ast, end_ast, body_ast, is_downto)

    def visit_call_statement(self, node: CallStatementNode) -> ProcCallASTNode:
        # procedure-call (Statement)
        
        proc_visitor = ProcFuncVisitor()
        proc_visitor.symbol_table = self.symbol_table
        proc_visitor.errors = self.errors
        
        return proc_visitor.visit_procedure_call(node)
        
    def visit_repeat_statement(self, node: RepeatStatementNode) -> RepeatASTNode:
        # repeat-statement
        
        condition_node = None
        statements = []
        
        for child in node.children:
            if isinstance(child, ExpressionNode):
                condition_node = child
            elif isinstance(child, ASTNode): 
                # Panggil dispatcher untuk setiap statement di dalam repeat
                stmt_ast = self.visit_statement(child)
                if stmt_ast:
                    if isinstance(stmt_ast, BlockASTNode):
                         statements.extend(stmt_ast.statements)
                    else:
                        statements.append(stmt_ast)
        
        expr_visitor = self._get_expression_visitor()
        cond_ast = expr_visitor.visit_expression(condition_node)
        
        if cond_ast.data_type is None:
             cond_ast.data_type = expr_visitor._infer_expression_type(cond_ast)

        if cond_ast.data_type != DataType.BOOLEAN:
            raise TypeMismatchError("BOOLEAN", cond_ast.data_type.name, "REPEAT UNTIL condition")
            
        return RepeatASTNode(statements, cond_ast)

    def _get_expression_visitor(self) -> ExpressionVisitor:
        # Helper: Membuat ExpressionVisitor dengan state symbol table yang sama.
        visitor = ExpressionVisitor()
        visitor.symbol_table = self.symbol_table
        visitor.errors = self.errors 
        return visitor