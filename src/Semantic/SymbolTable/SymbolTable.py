from Semantic.SymbolTable.ObjectType import *
from typing import List, Optional

class SymbolTable:
    def __init__(self):
        # tabel identifier utama
        self.tab: List[TabEntry] = []
        self.btab: List[BTabEntry] = []
        self.atab: List[ATabEntry] = []
        self.display: List[int] = [0]
        self.level: int = 0  
        
        # Tipe built-in yang tidak perlu dimasukkan dalam tab
        self.builtin_types = {
            "integer": DataType.INTEGER,
            "real": DataType.REAL,
            "boolean": DataType.BOOLEAN,
            "char": DataType.CHAR,
            "string": DataType.STRING
        }
        
        # Konstanta built-in yang tidak perlu disimpan di tab
        self.builtin_constants = {
            "true": (ObjectType.CONSTANT, DataType.BOOLEAN),
            "false": (ObjectType.CONSTANT, DataType.BOOLEAN)
        }
        
        # Inisialisasi reserved words dan prosedur built-in
        self.initialize_reserved()
        
    def initialize_reserved(self):
        # Reserved words Pascal-S (indeks 0–28)
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
        
        # Pastikan reserved words tepat 29
        assert len(reserved) == 29, f"Reserved words harus 29, tetapi ada {len(reserved)}"
        
        # Masukkan reserved words ke TAB (tidak punya blok / link)
        for identifier, obj, data_type in reserved:
            self.tab.append(TabEntry(identifier, obj, data_type, lev=0))
        
        # Inisialisasi blok global
        self.btab.append(BTabEntry())
        
        # Prosedur built-in standar
        builtin_procs = [
            ("writeln", ObjectType.PROCEDURE, DataType.VOID),
            ("write", ObjectType.PROCEDURE, DataType.VOID),
            ("readln", ObjectType.PROCEDURE, DataType.VOID),
            ("read", ObjectType.PROCEDURE, DataType.VOID),
        ]
        
        for identifier, obj, data_type in builtin_procs:
            # link menunjuk entry sebelumnya dalam blok yang sama
            link = self.btab[0].last
            entry = TabEntry(identifier, obj, data_type, ref=0, nrm=1, lev=0, adr=0, link=link)
            self.tab.append(entry)
            self.btab[0].last = len(self.tab) - 1
    
    def enter_program(self, program_name: str) -> int:
        # Masukkan nama program ke symbol table (global scope)
        link = self.btab[0].last
        entry = TabEntry(program_name, ObjectType.PROGRAM, DataType.VOID, 
                        ref=0, nrm=1, lev=0, adr=0, link=link)
        self.tab.append(entry)
        self.btab[0].last = len(self.tab) - 1
        return len(self.tab) - 1
    
    def enter_block(self):
        # Masuk ke blok baru
        self.level += 1
        new_block = BTabEntry()
        self.btab.append(new_block)
        self.display.append(len(self.btab)-1)
        return len(self.btab) - 1
    
    def exit_block(self):
        # Keluar dari blok saat ini
        if self.level > 0:
            self.level -= 1
            self.display.pop()
    
    def enter_identifier(self, identifier: str, obj: ObjectType, data_type: DataType, ref: int = 0, nrm: int = 1, adr: int = 0) -> int:
        # Memasukkan identifier (var, func, proc, dll) ke blok saat ini
        current_block_index = self.display[self.level]
        current_block = self.btab[current_block_index]
        
        # link mengacu ke identifier terakhir pada blok ini
        link = current_block.last
        
        entry = TabEntry(identifier, obj, data_type, ref, nrm, self.level, adr, link)
        self.tab.append(entry)
        current_block.last = len(self.tab) - 1
        
        # Jika variabel biasa, ukuran variabel bertambah
        if obj == ObjectType.VARIABLE:
            current_block.vsze += 1
        
        return len(self.tab) - 1
    
    def lookup_identifier(self, identifier: str) -> Optional[int]:
        # Mencari identifier di scope saat ini hingga scope parent
        if identifier.lower() in self.builtin_types:
            return -1 # Jika tipe built-in, return -1
        
        # Jika konstanta built-in, return -2
        if identifier.lower() in self.builtin_constants:
            return -2
        
        # Cari dari level aktif hingga level global
        for level in range(self.level, -1, -1):
            block_index = self.display[level]
            block = self.btab[block_index]
            
            # Traverse linked list pada blok
            current_index = block.last
            while current_index != 0:
                entry = self.tab[current_index]
                if entry.id.lower() == identifier.lower():
                    return current_index
                current_index = entry.link
        
        return None
    
    def is_builtin_type(self, identifier: str) -> bool:
        # Mengecek apakah keyword merupakan tipe built-in
        return identifier.lower() in self.builtin_types
    
    def is_builtin_constant(self, identifier: str) -> bool:
        # Mengecek apakah termasuk konstanta built-in
        return identifier.lower() in self.builtin_constants
    
    def get_builtin_constant_type(self, identifier: str) -> Optional[DataType]:
        # Mendapatkan DataType dari konstanta built-in
        const_info = self.builtin_constants.get(identifier.lower())
        return const_info[1] if const_info else None
    
    def is_builtin_procedure(self, identifier: str) -> bool:
        # Mengecek apakah prosedur built-in
        builtin_names = ['writeln', 'write', 'readln', 'read']
        return identifier.lower() in builtin_names
    
    def get_builtin_procedure_type(self, identifier: str) -> Optional[DataType]:
        # Prosedur built-in selalu bertipe VOID
        name = identifier.lower()
        if name in ['writeln', 'write', 'readln', 'read']:
            return DataType.VOID
        return None
    
    def enter_array(self, xtyp: DataType, etyp: DataType, eref: int, low: int, high: int, elsz: int) -> int:
        # Enter array ke tabel atab
        size = (high - low + 1) * elsz
        entry = ATabEntry(xtyp, etyp, eref, low, high, elsz, size)
        self.atab.append(entry)
        return len(self.atab) - 1
    
    def get_type_from_keyword(self, keyword: str) -> Optional[DataType]:
        return self.builtin_types.get(keyword.lower())
   
    def print_tables(self):
        # Menampilkan isi symbol table
        print("\n" + "=" * 90)
        print("| SYMBOL TABLE (TAB) - Identifier Table                          |")
        print("=" * 90)
        print("|{:>4} | {:20} | {:10} | {:7} | {:3} | {:3} | {:3} | {:3} | {:3} |".format(
            "Idx", "Identifier", "Object", "Type", "Ref", "Nrm", "Lev", "Adr", "Link"))
        print("|" + "-" * 88 + "|")
        
        has_identifiers = False
        for idx, entry in enumerate(self.tab):
            # Skip reserved words (0–28)
            if idx >= 29:
                has_identifiers = True
                type_str = str(entry.type.value) if hasattr(entry.type, 'value') else str(entry.type)
                obj_str = entry.obj.value if hasattr(entry.obj, 'value') else str(entry.obj)
                
                print("|{:>4} | {:20} | {:10} | {:7} | {:3} | {:3} | {:3} | {:3} | {:3} |".format(
                    idx, entry.id[:20], obj_str[:10], type_str[:7], 
                    entry.ref, entry.nrm, entry.lev, entry.adr, entry.link))
        
        if not has_identifiers:
            print("|{:^88}|".format("No user-defined identifiers"))
        
        print("=" * 90)
        print("Note: Reserved words (idx 0–28), built-in types, dan konstanta built-in tidak ditampilkan.")
        
        # BTAB
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
        
        # ATAB
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