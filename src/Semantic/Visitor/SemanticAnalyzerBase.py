from typing import Optional, List, Any
from Parser.ast import *
from src.Semantic.SymbolTable.SymbolTable import *
from src.Semantic.DecoratedAST.DecoratedASTNode import *
from src.Semantic.Visitor.SemanticError import *
from Repository.TokenType import TokenType
from Model.Token import Token

class SemanticAnalyzerBase:
    # Base class dengan utility methods untuk semantic analysis
    
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.current_function_return_type: Optional[DataType] = None
        self.errors: List[SemanticError] = []
    
    def _get_constant_value(self, token: Token) -> tuple:
        # Get constant value dan tipenya dari token
        if token.tokenType == TokenType.NUMBER:
            value = token.value
            if '.' in str(value):
                return float(value), DataType.REAL
            else:
                return int(value), DataType.INTEGER
        elif token.tokenType == TokenType.CHAR_LITERAL:
            return token.value, DataType.CHAR
        elif token.tokenType == TokenType.STRING_LITERAL:
            return token.value, DataType.STRING
        elif token.tokenType == TokenType.KEYWORD:
            if token.value.lower() == "true":
                return True, DataType.BOOLEAN
            elif token.value.lower() == "false":
                return False, DataType.BOOLEAN
        elif token.tokenType == TokenType.IDENTIFIER:
            # Lookup identifier (bisa reference ke konstanta lain)
            idx = self.symbol_table.lookup_identifier(token.value)
            if idx:
                entry = self.symbol_table.tab[idx]
                if entry.obj == ObjectType.CONSTANT:
                    return entry.adr, entry.type
        
        raise SemanticError(f"Invalid constant value: {token.value}")
    
    def _get_type_info(self, type_node) -> tuple:
        # Get type information dari TypeNode, return (DataType, ref)
        if isinstance(type_node, TypeNode):
            for child in type_node.children:
                if isinstance(child, Token) and child.tokenType == TokenType.KEYWORD:
                    data_type = self.symbol_table.get_type_from_keyword(child.value)
                    if data_type:
                        return data_type, 0
                elif isinstance(child, ArrayTypeNode):
                    return self._parse_array_type(child)
                elif isinstance(child, RecordTypeNode):
                    return self._parse_record_type(child)
                elif isinstance(child, RangeNode):
                    # Subrange type
                    return DataType.INTEGER, 0
                elif isinstance(child, Token) and child.tokenType == TokenType.IDENTIFIER:
                    # Custom type reference
                    idx = self.symbol_table.lookup_identifier(child.value)
                    if idx:
                        entry = self.symbol_table.tab[idx]
                        return entry.type, entry.ref
        
        return DataType.VOID, 0
    
    def _parse_array_type(self, node: ArrayTypeNode) -> tuple:
        low = 0
        high = 0
        element_type = DataType.INTEGER
        element_ref = 0
        
        for child in node.children:
            if isinstance(child, RangeNode):
                # Get range bounds
                range_values = []
                for range_child in child.children:
                    if isinstance(range_child, Token):
                        if range_child.tokenType == TokenType.NUMBER:
                            range_values.append(int(range_child.value))
                        elif range_child.tokenType == TokenType.RANGE_OPERATOR:
                            continue
                
                if len(range_values) >= 2:
                    low = range_values[0]
                    high = range_values[1]
            
            elif isinstance(child, TypeNode):
                element_type, element_ref = self._get_type_info(child)
        
        # Buat array entry di atab
        elsz = self._get_size(element_type, element_ref)
        array_ref = self.symbol_table.enter_array(
            DataType.INTEGER, element_type, element_ref, low, high, elsz
        )
        
        return DataType.ARRAY, array_ref
    
    def _parse_record_type(self, node: RecordTypeNode) -> tuple:
        # Parse record type definition
        # Buat block entry baru untuk record type ini
        record_block_index = self.symbol_table.enter_block()
        record_block = self.symbol_table.btab[record_block_index]
        
        # Parse semua deklarasi field dalam record
        total_size = 0
        field_offset = 0
        
        for child in node.children:
            if isinstance(child, VarDeclarationNode):
                # Ambil identifier field dan tipenya
                identifiers = []
                field_type = DataType.VOID
                field_ref = 0
                
                for var_child in child.children:
                    if isinstance(var_child, IdentifierListNode):
                        identifiers = self._get_identifier_list(var_child)
                    elif isinstance(var_child, TypeNode):
                        field_type, field_ref = self._get_type_info(var_child)
                
                # Hitung ukuran untuk tipe field ini
                field_size = self._get_size(field_type, field_ref)
                
                # Masukkan setiap field identifier ke symbol table
                for identifier in identifiers:
                    # Cek apakah field sudah ada dalam record ini
                    # Cari hanya di block saat ini untuk menghindari konflik
                    current_index = record_block.last
                    while current_index != 0:
                        entry = self.symbol_table.tab[current_index]
                        if entry.identifier.lower() == identifier.lower():
                            raise SemanticError(
                                f"Field '{identifier}' sudah dideklarasikan dalam record ini"
                            )
                        current_index = entry.link
                    
                    # Masukkan field sebagai variable di block record
                    # adr menyimpan offset field ini dalam record
                    field_index = self.symbol_table.enter_identifier(
                        identifier=identifier,
                        obj=ObjectType.VARIABLE,
                        data_type=field_type,
                        ref=field_ref,
                        nrm=1,  # Field normal (bukan by-reference)
                        adr=field_offset
                    )
                    
                    # Update offset untuk field berikutnya
                    field_offset += field_size
                    total_size += field_size
        
        # Update block entry dengan total ukuran semua field
        record_block.vsze = total_size
        record_block.lpar = 0  # Record tidak punya parameter
        
        # Keluar dari scope block record
        self.symbol_table.exit_block()
        
        # Return tipe RECORD dengan referensi ke block entry-nya
        return DataType.RECORD, record_block_index
        
    def _get_identifier_list(self, node: IdentifierListNode) -> List[str]:
        # Extract list of identifiers dari IdentifierListNode
        identifiers = []
        for child in node.children:
            if isinstance(child, Token) and child.tokenType == TokenType.IDENTIFIER:
                identifiers.append(child.value)
        return identifiers
    
    def _get_case_labels(self, node: CaseLabelListNode) -> List[Any]:
        # Extract case labels dari CaseLabelListNode
        labels = []
        for child in node.children:
            if isinstance(child, Token):
                if child.tokenType == TokenType.NUMBER:
                    labels.append(int(child.value))
                elif child.tokenType == TokenType.CHAR_LITERAL:
                    labels.append(child.value)
                elif child.tokenType == TokenType.IDENTIFIER:
                    # Could be constant reference
                    idx = self.symbol_table.lookup_identifier(child.value)
                    if idx:
                        entry = self.symbol_table.tab[idx]
                        if entry.obj == ObjectType.CONSTANT:
                            labels.append(entry.adr)
        return labels
    
    def _get_size(self, data_type: DataType, ref: int = 0) -> int:
        # Mengembalikan ukuran dari sebuah tipe data
        if data_type == DataType.INTEGER:
            return 1
        elif data_type == DataType.REAL:
            return 1
        elif data_type == DataType.BOOLEAN:
            return 1
        elif data_type == DataType.CHAR:
            return 1
        elif data_type == DataType.STRING:
            return 1
        elif data_type == DataType.ARRAY:
            # Untuk array, ambil ukuran dari tabel array (atab) jika referensi valid
            if ref > 0 and ref <= len(self.symbol_table.atab):
                return self.symbol_table.atab[ref - 1].size
            return 1
        elif data_type == DataType.RECORD:
            # Untuk record, hitung ukuran total berdasarkan tabel blok (btab)
            # Ukuran record = jumlah ukuran semua field (vsze)
            if ref > 0 and ref < len(self.symbol_table.btab):
                block_entry = self.symbol_table.btab[ref]
                return block_entry.vsze
            return 1
        else:
            # Default jika tipe tidak dikenali
            return 1
