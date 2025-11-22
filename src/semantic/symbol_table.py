from dataclasses import dataclass, field
from typing import Optional, List, Dict
from enum import Enum

class ObjectKind(Enum):
    """Kelas objek dalam tab"""
    CONSTANT = "constant"
    VARIABLE = "variable"
    TYPE = "type"
    PROCEDURE = "procedure"
    FUNCTION = "function"
    PROGRAM = "program"


class TypeKind(Enum):
    """Tipe dasar dalam Pascal-S"""
    NOTYPE = 0
    INTEGER = 1
    BOOLEAN = 2
    CHAR = 3
    REAL = 4
    ARRAY = 5
    STRING = 6

@dataclass
class TabEntry:
    """
    Entry untuk identifier table (tab)
    
    Attributes:
        identifier: Nama identifier
        link: Pointer ke identifier sebelumnya dalam scope yang sama (linked list per block)
        obj: Kelas objek (konstanta, variabel, tipe, prosedur, fungsi)
        type: Tipe dasar dari identifier
        ref: Pointer ke tabel lain jika tipe komposit (array/record)
        nrm: Normal variable (1) atau var parameter (0)
        lev: Lexical level (0=global, 1=dalam prosedur, dst)
        adr: Address/offset (bergantung jenis objek)
    """
    identifier: str
    link: int = 0
    obj: ObjectKind = ObjectKind.VARIABLE
    type: TypeKind = TypeKind.NOTYPE
    ref: int = 0
    nrm: int = 1  # 1 = normal, 0 = var parameter
    lev: int = 0
    adr: int = 0

    def __repr__(self):
        return (f"TabEntry(id='{self.identifier}', obj={self.obj.value}, "
                f"type={self.type.value}, lev={self.lev}, adr={self.adr})")

@dataclass
class ATabEntry:
    """
    Entry untuk array table (atab)
    
    Attributes:
        xtyp: Tipe indeks array
        etyp: Tipe elemen array
        eref: Pointer ke detail tipe elemen jika komposit
        low: Batas bawah indeks
        high: Batas atas indeks
        elsz: Ukuran satu elemen
        size: Total ukuran array
    """
    xtyp: TypeKind = TypeKind.INTEGER
    etyp: TypeKind = TypeKind.NOTYPE
    eref: int = 0
    low: int = 0
    high: int = 0
    elsz: int = 1
    size: int = 0

    def __repr__(self):
        return f"ATabEntry(xtyp={self.xtyp.value}, etyp={self.etyp.value}, [{self.low}..{self.high}], size={self.size})"

@dataclass
class BTabEntry:
    """
    Entry untuk block table (btab)
    
    Attributes:
        last: Pointer ke identifier terakhir di block ini
        lpar: Pointer ke parameter terakhir (untuk prosedur/fungsi)
        psze: Total ukuran parameter block
        vsze: Total ukuran variabel lokal block
    """
    last: int = 0
    lpar: int = 0
    psze: int = 0
    vsze: int = 0

    def __repr__(self):
        return f"BTabEntry(last={self.last}, lpar={self.lpar}, psze={self.psze}, vsze={self.vsze})"
    
class SymbolTable:

    def __init__(self):
        self.tab: List[TabEntry] = []
        self.atab: List[ATabEntry] = []
        self.btab: List[BTabEntry] = []

        self.display: List[int] = [0]  # Display untuk lexical levels
        self.current_level: int = 0  # Level lexical saat ini

        #counter
        self.tx: int = 0  # Index terakhir di tab
        self.ax: int = 0  # Index terakhir di atab
        self.bx: int = 0  # Index terakhir di btab

        self._init_reserved_idn()
        self._init_global_block()

    def _init_reserved_idn(self):
        """Inisialisasi reserved identifiers ke dalam symbol table"""
        reserved_idns = [
            ("INTEGER", ObjectKind.TYPE, TypeKind.INTEGER),
            ("BOOLEAN", ObjectKind.TYPE, TypeKind.BOOLEAN),
            ("CHAR", ObjectKind.TYPE, TypeKind.CHAR),
            ("REAL", ObjectKind.TYPE, TypeKind.REAL),
            ("TRUE", ObjectKind.CONSTANT, TypeKind.BOOLEAN),
            ("FALSE", ObjectKind.CONSTANT, TypeKind.BOOLEAN),
        ]
        for name, obj_kind, type_kind in reserved_idns:
            entry = TabEntry(
                identifier=name,
                obj=obj_kind,
                type=type_kind,
                lev=0,
                adr=0
            )
            self.tab.append(entry)
            self.tx += 1