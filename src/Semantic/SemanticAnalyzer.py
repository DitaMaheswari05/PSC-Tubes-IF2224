from typing import List, Optional
from Parser.ast import *
from Semantic.Visitor.SemanticAnalyzerBase import SemanticAnalyzerBase
from Semantic.Visitor.SemanticError import *
from Semantic.SymbolTable.SymbolTable import *
from Semantic.DecoratedAST.DecoratedASTNode import *
from Semantic.Visitor.StatementVisitor import StatementVisitor
from Semantic.Visitor.DeclarationVisitor import DeclarationVisitor
from Semantic.Visitor.ExpressionVisitor import ExpressionVisitor
from Semantic.Visitor.ArrayAccessVisitor import ArrayAccessVisitor
from Semantic.Visitor.ProcFuncVisitor import ProcFuncVisitor
from Repository.TokenType import TokenType
from Model.Token import Token

class SemanticAnalyzer(SemanticAnalyzerBase):
    def __init__(self):
        super().__init__()
        # Inisialisasi semua visitor untuk berbagai jenis node
        self.declaration_visitor = DeclarationVisitor()
        self.statement_visitor = StatementVisitor()
        self.expression_visitor = ExpressionVisitor()
        self.array_visitor = ArrayAccessVisitor()
        self.proc_func_visitor = ProcFuncVisitor()
        
        # Share symbol table ke semua visitor agar semua visitor menggunakan symbol table yang sama
        for visitor in [self.declaration_visitor, self.statement_visitor, 
                       self.expression_visitor, self.array_visitor, 
                       self.proc_func_visitor]:
            visitor.symbol_table = self.symbol_table
    
    def analyze(self, parse_tree: ProgramNode) -> ProgramASTNode:
        # Main entry point untuk semantic analysis
        # Input: Parse tree dari syntax parser
        # Output: Decorated AST dengan anotasi tipe dan symbol table reference
        
        try:
            # Visit program node (root)
            decorated_ast = self.visit_program(parse_tree)
            
            # Return decorated AST
            return decorated_ast
        
        except SemanticError as e:
            # Tampilkan error dan re-raise
            print(f"\n{e}")
            self.errors.append(e)
            raise
    
    def visit_program(self, node: ProgramNode) -> ProgramASTNode:
        # Visit program root
        # Production: <program> → <program-header> <declaration-part> <compound-statement> DOT
        
        # Ambil nama program dari program header
        program_name = ""
        for child in node.children:
            if isinstance(child, ProgramHeaderNode):
                for header_child in child.children:
                    if isinstance(header_child, Token) and header_child.tokenType == TokenType.IDENTIFIER:
                        program_name = header_child.value
                        break
        
        # Masukkan nama program ke symbol table (Global Entry)
        program_idx = self.symbol_table.enter_identifier(
            identifier=program_name,
            obj=ObjectType.PROGRAM,
            data_type=DataType.VOID,
            ref=0,  # ref ke btab[0]
            nrm=1,
            adr=0
        )
        
        # Update btab[0].last untuk menunjuk ke program entry
        self.symbol_table.btab[0].last = program_idx
        
        # Buat ProgramASTNode
        program_ast = ProgramASTNode(program_name)
        program_ast.annotate(
            data_type=DataType.VOID,
            tab_index=program_idx,
            block_index=0,
            scope_level=0
        )
        
        # Process children: declarations dan compound statement
        for child in node.children:
            # Skip program header dan DOT token
            if isinstance(child, ProgramHeaderNode):
                continue
            if isinstance(child, Token) and child.tokenType == TokenType.DOT:
                continue
            
            # Process declaration part
            if isinstance(child, DeclarationPartNode):
                # Visit deklarasi. Ini akan mengisi Symbol Table di Level 0 (Global)
                declarations = self.declaration_visitor.visit_declaration_part(child)
                program_ast.declarations.extend(declarations)
            
            # Process compound statement (main block)
            elif isinstance(child, CompoundStatementNode):
                # Visit compound statement
                block_ast = self.statement_visitor.visit_compound_statement(child)
                
                block_ast.annotate(
                    block_index=0, # Selalu 0 untuk Global Block
                    scope_level=self.symbol_table.level # Seharusnya 0
                )
                program_ast.block = block_ast
        
        return program_ast
    
    def get_symbol_table(self) -> SymbolTable:
        # Return symbol table untuk inspection atau code generation
        return self.symbol_table
    
    def get_errors(self) -> List[SemanticError]:
        # Return list of semantic errors yang ditemukan
        return self.errors
    
    def print_symbol_tables(self):
        # Print semua symbol tables untuk debugging
        self.symbol_table.print_tables()
    
    def has_errors(self) -> bool:
        # Cek apakah ada semantic errors
        return len(self.errors) > 0