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
            ("", ObjectType.CONSTANT, DataType.VOID),
            ("integer", ObjectType.TYPE, DataType.INTEGER),
            ("real", ObjectType.TYPE, DataType.REAL),
            ("boolean", ObjectType.TYPE, DataType.BOOLEAN),
            ("char", ObjectType.TYPE, DataType.CHAR),
            ("string", ObjectType.TYPE, DataType.STRING),
            ("true", ObjectType.CONSTANT, DataType.BOOLEAN),
            ("false", ObjectType.CONSTANT, DataType.BOOLEAN),
            ("writeln", ObjectType.PROCEDURE, DataType.VOID),
            ("write", ObjectType.PROCEDURE, DataType.VOID),
            ("readln", ObjectType.PROCEDURE, DataType.VOID),
            ("read", ObjectType.PROCEDURE, DataType.VOID),
        ]
        
        # Tambahkan placeholder hingga indeks 29
        while len(reserved) < 29:
            reserved.append(("", ObjectType.CONSTANT, DataType.VOID))
        
        for identifier, obj, data_type in reserved:
            self.tab.append(TabEntry(identifier, obj, data_type, lev=0))
        
        # Inisialisasi global block (btab[0])
        self.btab.append(BTabEntry())
    
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
    
   
   
    # buat debug isi dari tab, atab, btab 
    def print_tables(self):
        # TAB TABLE
        print("\n" + "=" * 90)
        print("| SYMBOL TABLE (TAB) - Identifier Table                                             |")
        print("=" * 90)
        print("|{:>4} | {:20} | {:10} | {:7} | {:3} | {:3} | {:3} | {:3} | {:3} |".format(
            "Idx", "Identifier", "Object", "Type", "Ref", "Nrm", "Lev", "Adr", "Link"))
        print("|" + "-" * 88 + "|")
        
        for idx, entry in enumerate(self.tab):
            if idx < 29:  # Skip reserved words
                continue
            type_str = str(entry.type.value) if hasattr(entry.type, 'value') else str(entry.type)
            obj_str = entry.obj.value if hasattr(entry.obj, 'value') else str(entry.obj)
            print("|{:>4} | {:20} | {:10} | {:7} | {:3} | {:3} | {:3} | {:3} | {:3} |".format(
                idx, entry.id[:20], obj_str[:10], type_str[:7], entry.ref, entry.nrm, entry.lev, entry.adr, entry.link))
        
        print("=" * 90)
        
        # BTAB TABLE
        print("\n" + "=" * 60)
        print("| BLOCK TABLE (BTAB)                                            |")
        print("=" * 60)
        print("|{:>4} | {:7} | {:7} | {:7} | {:7} |".format("Idx", "Last", "Lpar", "Psze", "Vsze"))
        print("|" + "-" * 58 + "|")
        
        for idx, entry in enumerate(self.btab):
            print("|{:>4} | {:7} | {:7} | {:7} | {:7} |".format(
                idx, entry.last, entry.lpar, entry.psze, entry.vsze))
        
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
            
            print("=" * 80)