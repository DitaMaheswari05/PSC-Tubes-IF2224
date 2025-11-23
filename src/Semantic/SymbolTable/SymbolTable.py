from src.Semantic.SymbolTable.ObjectType import *
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
                if entry.identifier.lower() == identifier.lower():
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
        print("\n=== TAB (Identifier Table) ===")
        print(f"{'Idx':<5} {'Identifier':<15} {'Obj':<12} {'Type':<10} {'Ref':<5} {'Nrm':<5} {'Lev':<5} {'Adr':<5} {'Link':<5}")
        print("-" * 80)
        for idx, entry in enumerate(self.tab):
            if idx < 29:  # Skip reserved
                continue
            print(f"{idx:<5} {entry.identifier:<15} {entry.obj.value:<12} {entry.type.value:<10} {entry.ref:<5} {entry.nrm:<5} {entry.lev:<5} {entry.adr:<5} {entry.link:<5}")
        
        print("\n=== BTAB (Block Table) ===")
        print(f"{'Idx':<5} {'Last':<10} {'Lpar':<10} {'Psze':<10} {'Vsze':<10}")
        print("-" * 50)
        for idx, entry in enumerate(self.btab):
            print(f"{idx:<5} {entry.last:<10} {entry.lpar:<10} {entry.psze:<10} {entry.vsze:<10}")
        
        if self.atab:
            print("\n=== ATAB (Array Table) ===")
            print(f"{'Idx':<5} {'Xtyp':<10} {'Etyp':<10} {'Eref':<5} {'Low':<5} {'High':<5} {'Elsz':<5} {'Size':<5}")
            print("-" * 60)
            for idx, entry in enumerate(self.atab):
                print(f"{idx:<5} {entry.xtyp.value:<10} {entry.etyp.value:<10} {entry.eref:<5} {entry.low:<5} {entry.high:<5} {entry.elsz:<5} {entry.size:<5}")