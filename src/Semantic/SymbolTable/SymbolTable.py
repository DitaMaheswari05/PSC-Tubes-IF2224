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
        
        # Set untuk melacak built-in procedures yang sudah dimasukkan ke tab
        self.registered_builtins: set = set()
        
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
        
        # # Prosedur built-in standar
        # builtin_procs = [
        #     ("writeln", ObjectType.PROCEDURE, DataType.VOID),
        #     # ("write", ObjectType.PROCEDURE, DataType.VOID),
        #     # ("readln", ObjectType.PROCEDURE, DataType.VOID),
        #     # ("read", ObjectType.PROCEDURE, DataType.VOID),
        # ]
        
        # for identifier, obj, data_type in builtin_procs:
        #     # link=0 karena built-in tidak masuk linked list btab
        #     entry = TabEntry(identifier, obj, data_type, ref=0, nrm=1, lev=0, adr=0, link=0)
        #     self.tab.append(entry)
    
    def enter_program(self, program_name: str) -> int:
        # Program name tidak masuk linked list
        entry = TabEntry(program_name, ObjectType.PROGRAM, DataType.VOID, 
                        ref=0, nrm=1, lev=0, adr=0, link=0)
        self.tab.append(entry)
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
        current_block_index = self.display[self.level]
        current_block = self.btab[current_block_index]
        
        # Link ke entry sebelumnya dalam scope yang sama
        # Jika ini entry pertama dalam scope, link=0
        # Jika sudah ada entry sebelumnya, link ke entry terakhir yang valid (bukan program)
        link_to_previous = 0
        if current_block.last != 0:
            last_entry = self.tab[current_block.last]
            # Hanya link jika entry terakhir bukan program
            if last_entry.obj != ObjectType.PROGRAM:
                link_to_previous = current_block.last
        
        entry = TabEntry(identifier, obj, data_type, ref, nrm, self.level, adr, link=link_to_previous)
        self.tab.append(entry)
        new_idx = len(self.tab) - 1
        
        # Update last ke entry baru
        current_block.last = new_idx
        
        # Jika variabel biasa, ukuran variabel bertambah
        if obj == ObjectType.VARIABLE:
            current_block.vsze += 1
        
        return new_idx
    
    def enter_builtin_procedure(self, name: str) -> int:
        # Cek apakah sudah pernah dimasukkan
        if name.lower() in self.registered_builtins:
            # Cari indeks-nya di TAB
            for idx in range(29, len(self.tab)):
                if self.tab[idx].id.lower() == name.lower():
                    return idx
        
        # Masukkan ke tab dengan link=0 (tidak masuk linked list)
        entry = TabEntry(name, ObjectType.PROCEDURE, DataType.VOID, 
                        ref=0, nrm=1, lev=0, adr=0, link=0)
        self.tab.append(entry)
        
        # Tandai sudah diregistrasi
        self.registered_builtins.add(name.lower())
        
        return len(self.tab) - 1
    
    
    def lookup_identifier(self, identifier: str) -> Optional[int]:
        # Cek apakah identifier adalah tipe built-in (integer, real, boolean, dll)
        if identifier.lower() in self.builtin_types:
            return -1
        
        # Cek apakah identifier adalah konstanta built-in (true, false)
        if identifier.lower() in self.builtin_constants:
            return -2
        
        # Cari identifier dari level saat ini hingga level global (0)
        for level in range(self.level, -1, -1):
            block_index = self.display[level]
            block = self.btab[block_index]
            
            # Mulai dari entry terakhir di blok (backward linked list)
            current_idx = block.last
            while current_idx is not None and current_idx != 0:
                entry = self.tab[current_idx]
                # Skip jika ketemu program name
                if entry.obj == ObjectType.PROGRAM:
                    break
                # Bandingkan nama identifier (case-insensitive)
                if entry.id.lower() == identifier.lower():
                    return current_idx
                # Ikuti link ke entry sebelumnya
                current_idx = entry.link if entry.link != 0 else None
        
        # Jika tidak ditemukan, cek apakah prosedur built-in (writeln, dll)
        if self.is_builtin_procedure(identifier):
            return self.enter_builtin_procedure(identifier)
        
        # Identifier tidak ditemukan
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
        builtin_names = ['writeln']
        return identifier.lower() in builtin_names
    
    def get_builtin_procedure_type(self, identifier: str) -> Optional[DataType]:
        # Prosedur built-in selalu bertipe VOID
        if self.is_builtin_procedure(identifier):
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
                
                identifier_display = entry.id[:20]
                if entry.obj == ObjectType.PROCEDURE and entry.lev == 0 and self.is_builtin_procedure(entry.id):
                    identifier_display = f"{entry.id[:12]} (predefined)"
                
                print("|{:>4} | {:20} | {:10} | {:7} | {:3} | {:3} | {:3} | {:3} | {:3} |".format(
                    idx, identifier_display, obj_str[:10], type_str[:7], 
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