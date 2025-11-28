from enum import Enum

class ObjectType(Enum):
    PROGRAM = "program"
    CONSTANT = "constant"
    VARIABLE = "variable"
    TYPE = "type"
    PROCEDURE = "procedure"
    FUNCTION = "function"
    PARAMETER = "parameter"

class DataType(Enum):
    INTEGER = 1
    REAL = 2
    BOOLEAN = 3
    CHAR = 4
    STRING = 5
    ARRAY = 6
    RECORD = 7
    VOID = 0

# Identifier table (tab)
class TabEntry:
    def __init__(self, identifier: str, obj: ObjectType, data_type: DataType, ref: int = 0, nrm: int = 1, lev: int = 0, adr: int = 0, link: int = 0):
        self.id = identifier
        self.obj = obj
        self.type = data_type
        self.ref = ref
        self.nrm = nrm
        self.lev = lev
        self.adr = adr
        self.link = link
    
    def __repr__(self):
        return f"TabEntry(id={self.id}, obj={self.obj.value}, type={self.type.value}, ref={self.ref}, nrm={self.nrm}, lev={self.lev}, adr={self.adr}, link={self.link})"

# Block table (btab)
class BTabEntry:
    def __init__(self, last: int = 0, lpar: int = 0, psze: int = 0, vsze: int = 0):
        self.last = last
        self.lpar = lpar
        self.psze = psze
        self.vsze = vsze
    
    def __repr__(self):
        return f"BTabEntry(last={self.last}, lpar={self.lpar}, psze={self.psze}, vsze={self.vsze})"

# Array Type Table (atab)
class ATabEntry:
    def __init__(self, xtyp: DataType, etyp: DataType, eref: int = 0, 
                 low: int = 0, high: int = 0, elsz: int = 1, size: int = 0):
        self.xtyp = xtyp
        self.etyp = etyp
        self.eref = eref
        self.low = low
        self.high = high
        self.elsz = elsz
        self.size = size
    
    def __repr__(self):
        return f"ATabEntry(xtyp={self.xtyp.value}, etyp={self.etyp.value}, eref={self.eref}, low={self.low}, high={self.high}, elsz={self.elsz}, size={self.size})"
