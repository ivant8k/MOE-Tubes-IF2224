from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
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
        # reserved_idns = [
        #     ("INTEGER", ObjectKind.TYPE, TypeKind.INTEGER),
        #     ("BOOLEAN", ObjectKind.TYPE, TypeKind.BOOLEAN),
        #     ("CHAR", ObjectKind.TYPE, TypeKind.CHAR),
        #     ("REAL", ObjectKind.TYPE, TypeKind.REAL),
        #     ("TRUE", ObjectKind.CONSTANT, TypeKind.BOOLEAN),
        #     ("FALSE", ObjectKind.CONSTANT, TypeKind.BOOLEAN),
        # ]
        # for name, obj_kind, type_kind in reserved_idns:
        #     entry = TabEntry(
        #         identifier=name,
        #         obj=obj_kind,
        #         type=type_kind,
        #         lev=0,
        #         adr=0
        #     )
        #     self.tab.append(entry)
        #     self.tx += 1

        # Mapping tipe dasar ke nilai enum TypeKind
        reserved_types = [
            ("INTEGER", TypeKind.INTEGER),
            ("BOOLEAN", TypeKind.BOOLEAN),
            ("CHAR",    TypeKind.CHAR),
            ("REAL",    TypeKind.REAL),
        ]
        
        reserved_consts = [
            ("TRUE",  TypeKind.BOOLEAN, 1),
            ("FALSE", TypeKind.BOOLEAN, 0),
        ]

        # Masukkan Tipe
        for name, kind in reserved_types:
            self.enter(name, ObjectKind.TYPE, kind, 0, 1, 0, 0);

        # Masukkan Konstanta
        for name, kind, value in reserved_consts:
            self.enter(name, ObjectKind.CONSTANT, kind, 0, 1, 0, value);

    def _init_global_block(self):
        """Membuat block global (program) di btab[0]"""
        # Entry btab pertama buat global scope
        self.btab.append(TabEntry(last=0, lpar=0, psze=0, vsze=0))
        self.bx = 0
        self.display.append(0)  # Level 0 di display

        # Update 'last' di btab[0] bair nunjuk ke last identifier, yaitu reserved words (asumsi di level 0)
        self.btab[0].last = self.tx

    def enter(self, name:str, obj:ObjectKind, type_kind:TypeKind, ref:int, nrm:int, lev:int, adr:int) -> int:
        """
        Generic method untuk memasukkan entry baru ke 'tab'.
        Akan mengembalikan index entry baru di tab.
        Insert di ujung tab, abis itu update link dari btab
        Args:
            name (str): Nama identifier
            obj (ObjectKind): Kelas objek
            type_kind (TypeKind): Tipe dasar
            ref (int): Pointer ke tabel lain jika komposit
            nrm (int): Normal variable (1) atau var parameter (0)
            lev (int): Lexical level
            adr (int): Address/offset
        """
        # bikin object TabEntry
        new_entry = TabEntry(
            identifier=name,
            link = 0, # nanti diupdate sama semantic analyzer
            obj=obj,
            type=type_kind,
            ref=ref,
            nrm=nrm,
            lev=lev,
            adr=adr
        )
        self.tab.append(new_entry)
        self.tx += 1
        current_idx = self.tx

        # Update link
        if len(self.display) > 0:
            # Ambil index btab untuk level saat ini
            btab_idx = self.display[lev] if lev < len(self.display) else self.display[-1]

            # Link entry baru yang nunjuk ke variable terakhir di scope ini
            self.tab[current_idx].link = self.btab[btab_idx].last

            # Update last pointer di btab biar nunjuk ke entry baru
            self.btab[btab_idx].last =current_idx

        return current_idx  # Kembalikan index entry baru
    
    def add_variable(self, name:str, type_kind: TypeKind, ref: int = 0):
        """
        Menambah variabel ke scope saat ini.
        Penting buat Code Generation karena Compiler perlu tahu di alamat memori relatif keberapa (offset) sebuah variabel disimpan dalam stack frame.
        Args:
            name (str): Nama variabel
            type_kind (TypeKind): Tipe dasar variabel
            ref (int): Pointer ke tabel lain jika komposit
        """
        # Cek duplikasi
        if self.lookup_local(name) != 0:
            raise ValueError(f"Duplicate identifier '{name}' in the same scope.")
        
        current_btab_idx = self.display[self.current_level]

        size = 1
        if type_kind == TypeKind.ARRAY:
            size = self.atab[ref-1].size # ref-1 karena ref biasanya 1-based index

        current_disp = self.btab[current_btab_idx].vsze
        self.enter(
            name=name,
            obj=ObjectKind.VARIABLE,
            type_kind=type_kind,
            ref=ref,
            nrm=1,
            lev=self.current_level,
            adr=current_disp
        )

        # Update ukuran variabel lokal di block ini
        self.btab[current_btab_idx].vsze += size

    def add_constant(self, name: str, type_kind: TypeKind, value: Any):
        """Deklarasi Konstanta"""
        self.enter(
            name=name,
            obj=ObjectKind.CONSTANT,
            type_kind=type_kind,
            ref=0,
            nrm=1,
            lev=self.current_level,
            adr=value  # Simpan nilai konstanta di adr
        )

    def enter_scope(self, scope_name: str):
        """
        Masuk ke scope baru (Procedure/Function).
        Membuat entry baru di btab dan update display.
        """
        self.current_level += 1

        # Buat entry block baru
        self.btab.append(BTabEntry(last=0, lpar=0, psze=0, vsze=0))
        self.bx += 1

        # Update display
        if len(self.display) <= self.current_level:
            self.display.append(self.bx)
        else:
            self.display[self.current_level] = self.bx

    def exit_scope(self):
        """
        Keluar dari scope saat ini.
        Cuma menurunkan level lexical dan reset display
        """
        if self.current_level > 0:
            self.display[self.current_level] = 0 # Reset
            self.current_level -= 1

    def lookup(self, name: str) -> int:
        """
        Implementasi dari aturan Static Scoping dan Shadowing.
        Mencari identifier mulai dari scope terdalam ke global.
        Mengembalikan index di tab, atau 0 jika tidak ditemukan.
        args:
            name (str): Nama identifier yang dicari
        """
        for lev in range(self.current_level, -1, -1):
            btab_idx = self.display[lev]
            curr = self.btab[btab_idx].last # mulai dari identifier terakhir di block ini
            # Transverse linked list (field 'link')
            while curr > 0: # 0 dianggap null/sentinel
                entry = self.tab[curr]
                if entry.identifier == name:
                    return curr # Ditemukan
                curr = entry.link

        return 0  # Tidak ditemukan

    def lookup_local (self, name: str) -> int:
        """
        Pencarian identifier khusus validasi deklarasi
        Lookup biasa akan memprotes kalo x global sudah ada -> padahal kita mau deklarasi x lokal
        """
        btab_idx = self.display[self.current_level]
        curr = self.btab[btab_idx].last
        while curr > 0:
            entry = self.tab[curr]
            if entry.identifier == name:
                return curr
            curr = entry.link
        return 0
    
    def get_entry(self, idx: int) -> Optional[TabEntry]:
        """
        Safety Wrapper biar ga crash kalo indexnya invalid (ada boundary check)
        Mengambil TabEntry berdasarkan index di tab
        Args:
            idx (int): Index di tab"""
        if 0 < idx <= self.tx:
            return self.tab[idx]
        return None