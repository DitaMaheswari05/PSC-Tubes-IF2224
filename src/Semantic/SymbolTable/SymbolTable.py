from Semantic.SymbolTable.ObjectType import *
from typing import List, Optional

class SymbolTable:
    def __init__(self):
        self.tab: List[TabEntry] = []
        self.btab: List[BTabEntry] = []
        self.atab: List[ATabEntry] = []
        self.display: List[int] = [0]
        self.level: int = 0  
        
        self.initialize_reserved()
        
    def initialize_reserved(self):
        reserved = [
            ("and", ObjectType.CONSTANT, DataType.VOID),
            ("array", ObjectType.CONSTANT, DataType.VOID),
            ("begin", ObjectType.CONSTANT, DataType.VOID),
            ("case", ObjectType.CONSTANT, DataType.VOID),
            ("const", ObjectType.CONSTANT, DataType.VOID),
            ("div", ObjectType.CONSTANT, DataType.VOID),
            ("downto", ObjectType.CONSTANT, DataType.VOID),
            ("do", ObjectType.CONSTANT, DataType.VOID),
            ("else", ObjectType.CONSTANT, DataType.VOID),
            ("end", ObjectType.CONSTANT, DataType.VOID),
            ("for", ObjectType.CONSTANT, DataType.VOID),
            ("function", ObjectType.CONSTANT, DataType.VOID),
            ("if", ObjectType.CONSTANT, DataType.VOID),
            ("mod", ObjectType.CONSTANT, DataType.VOID),
            ("not", ObjectType.CONSTANT, DataType.VOID),
            ("of", ObjectType.CONSTANT, DataType.VOID),
            ("or", ObjectType.CONSTANT, DataType.VOID),
            ("procedure", ObjectType.CONSTANT, DataType.VOID),
            ("program", ObjectType.CONSTANT, DataType.VOID),
            ("record", ObjectType.CONSTANT, DataType.VOID),
            ("repeat", ObjectType.CONSTANT, DataType.VOID),
            ("string", ObjectType.TYPE, DataType.STRING),
            ("then", ObjectType.CONSTANT, DataType.VOID),
            ("to", ObjectType.CONSTANT, DataType.VOID),
            ("type", ObjectType.CONSTANT, DataType.VOID),
            ("until", ObjectType.CONSTANT, DataType.VOID),
            ("var", ObjectType.CONSTANT, DataType.VOID),
            ("while", ObjectType.CONSTANT, DataType.VOID),
            ("packed", ObjectType.CONSTANT, DataType.VOID),
        ]

        
        # Pastikan ada tepat 29 reserved words (indeks 0-28)
        assert len(reserved) == 29, f"Reserved words harus 29, tetapi ada {len(reserved)}"
        
        # Tambahkan reserved words ke tab
        for identifier, obj, data_type in reserved:
            self.tab.append(TabEntry(identifier, obj, data_type, lev=0))
        
        # Inisialisasi btab[0] untuk global block
        self.btab.append(BTabEntry())
        
        # Tambahkan tipe data built-in setelah reserved words (indeks 29+)
        builtin_types = [
            ("integer", ObjectType.TYPE, DataType.INTEGER),
            ("real", ObjectType.TYPE, DataType.REAL),
            ("boolean", ObjectType.TYPE, DataType.BOOLEAN),
            ("char", ObjectType.TYPE, DataType.CHAR),
            # string sudah ada di reserved words (indeks 21)
        ]
        
        for identifier, obj, data_type in builtin_types:
            self.tab.append(TabEntry(identifier, obj, data_type, lev=0))
        
        # Tambahkan konstanta boolean setelah tipe data
        boolean_constants = [
            ("true", ObjectType.CONSTANT, DataType.BOOLEAN),
            ("false", ObjectType.CONSTANT, DataType.BOOLEAN),
        ]
        
        for identifier, obj, data_type in builtin_types:
            link = self.btab[0].last  # Link ke entry sebelumnya di block ini
            entry = TabEntry(identifier, obj, data_type, ref=0, nrm=1, lev=0, adr=0, link=link)
            self.tab.append(entry)
            self.btab[0].last = len(self.tab) - 1  # Update last pointer
        
        # Tambahkan konstanta boolean setelah tipe data
        boolean_constants = [
            ("true", ObjectType.CONSTANT, DataType.BOOLEAN),
            ("false", ObjectType.CONSTANT, DataType.BOOLEAN),
        ]
        
        for identifier, obj, data_type in boolean_constants:
            link = self.btab[0].last  # Link ke entry sebelumnya di block ini
            entry = TabEntry(identifier, obj, data_type, ref=0, nrm=1, lev=0, adr=0, link=link)
            self.tab.append(entry)
            self.btab[0].last = len(self.tab) - 1  # Update last pointer
    
    def enter_block(self):
        self.level += 1
        new_block = BTabEntry()
        self.btab.append(new_block)
        self.display.append(len(self.btab)-1)
        return len(self.btab) - 1
    
    def exit_block(self):
        if self.level > 0:
            self.level -= 1
            self.display.pop()
    
    # masukan identifier baru ke tab
    def enter_identifier (self, identifier: str, obj: ObjectType, data_type: DataType, ref: int = 0, nrm: int = 1, adr: int = 0) -> int :
        current_block_index = self.display[self.level]
        current_block = self.btab[current_block_index]
        
        # hubungkan ke identifier sebelumnya di blok yang sama
        link = current_block.last
        
        entry = TabEntry(identifier, obj, data_type, ref, nrm, self.level, adr, link)
        self.tab.append(entry)
        current_block.last = len(self.tab) - 1
        
        return len(self.tab) - 1
    
    # cari identifier dalam scope saat ini dan parent scope
    def lookup_identifier(self, identifier: str) -> Optional[int]:
        
        # cari dari level saat ini ke level 0
        for level in range(self.level, -1, -1):
            block_index = self.display[level]
            block = self.btab[block_index]
            
            # traverse linked list di block ini
            current_index = block.last
            while current_index != 0:
                entry = self.tab[current_index]
                if entry.id.lower() == identifier.lower():
                    return current_index
                current_index = entry.link
        return None
    
    def is_builtin_procedure(self, identifier: str) -> bool:
        # Cek apakah identifier adalah built-in procedure/function.
        # Built-in: writeln, write, readln, read
        builtin_names = ['writeln', 'write', 'readln', 'read']
        return identifier.lower() in builtin_names
    
    def get_builtin_procedure_type(self, identifier: str) -> Optional[DataType]:
        # Procedures mengembalikan VOID.
        name = identifier.lower()
        if name in ['writeln', 'write', 'readln', 'read']:
            return DataType.VOID  # All are procedures
        return None
    
    # masukan entri array baru ke atab
    def enter_array(self, xtyp: DataType, etyp: DataType, eref: int, low: int, high: int, elsz: int) -> int :
        size = (high - low + 1) * elsz
        entry = ATabEntry(xtyp, etyp, eref, low, high, elsz, size)
        self.atab.append(entry)
        return len(self.atab) - 1
    
    
    def get_type_from_keyword(self, keyword: str) -> Optional[DataType]:
        type_map = {
            "integer": DataType.INTEGER,
            "real": DataType.REAL,
            "boolean": DataType.BOOLEAN,
            "char": DataType.CHAR,
            "string": DataType.STRING
        }
        return type_map.get(keyword.lower())
   
    # Print tabel tab, atab, btab 
    def print_tables(self):
        print("\n" + "=" * 90)
        print("| SYMBOL TABLE (TAB) - Identifier Table (User-defined only)                         |")
        print("=" * 90)
        print("|{:>4} | {:20} | {:10} | {:7} | {:3} | {:3} | {:3} | {:3} | {:3} |".format(
            "Idx", "Identifier", "Object", "Type", "Ref", "Nrm", "Lev", "Adr", "Link"))
        print("|" + "-" * 88 + "|")
        
        has_identifiers = False
        for idx, entry in enumerate(self.tab):
            if idx >= 29:
                has_identifiers = True
                type_str = str(entry.type.value) if hasattr(entry.type, 'value') else str(entry.type)
                obj_str = entry.obj.value if hasattr(entry.obj, 'value') else str(entry.obj)
                
                print("|{:>4} | {:20} | {:10} | {:7} | {:3} | {:3} | {:3} | {:3} | {:3} |".format(
                    idx, entry.id[:20], obj_str[:10], type_str[:7], entry.ref, entry.nrm, entry.lev, entry.adr, entry.link))
        
        if not has_identifiers:
            print("|{:^88}|".format("No user-defined identifiers"))
        
        print("=" * 90)
        print("Note: Reserved words (idx 0-28) are hidden. User identifiers start from idx 29.")
        
        # BTAB TABLE
        print("\n" + "=" * 60)
        print("| BLOCK TABLE (BTAB)                                       |")
        print("=" * 60)
        print("|{:>4} | {:7} | {:7} | {:7} | {:7} |".format("Idx", "Last", "Lpar", "Psze", "Vsze"))
        print("|" + "-" * 58 + "|")
        
        for idx, entry in enumerate(self.btab):
            print("|{:>4} | {:7} | {:7} | {:7} | {:7} |".format(
                idx, entry.last, entry.lpar, entry.psze, entry.vsze))
        
        print("|" + "-" * 58 + "|")
        print("=" * 60)
        
        # ATAB TABLE (if exists)
        if self.atab:
            print("\n" + "=" * 80)
            print("| ARRAY TABLE (ATAB)                                                              |")
            print("=" * 80)
            print("|{:>4} | {:7} | {:7} | {:5} | {:5} | {:5} | {:5} | {:6} |".format(
                "Idx", "Xtyp", "Etyp", "Eref", "Low", "High", "Elsz", "Size"))
            print("|" + "-" * 78 + "|")
            
            for idx, entry in enumerate(self.atab):
                xtyp_str = str(entry.xtyp.value) if hasattr(entry.xtyp, 'value') else str(entry.xtyp)
                etyp_str = str(entry.etyp.value) if hasattr(entry.etyp, 'value') else str(entry.etyp)
                print("|{:>4} | {:7} | {:7} | {:5} | {:5} | {:5} | {:5} | {:6} |".format(
                    idx, xtyp_str, etyp_str, entry.eref, entry.low, entry.high, entry.elsz, entry.size))
            
            print("|" + "-" * 78 + "|")
            print("=" * 80)