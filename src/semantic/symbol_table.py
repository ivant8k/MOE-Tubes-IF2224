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
        self.tab: List[TabEntry] = [TabEntry(identifier="__DUMMY__")]  # index 0 dummy
        self.atab: List[ATabEntry] = [ATabEntry()]  # index 0 dummy
        self.btab: List[BTabEntry] = [BTabEntry()]  # index 0 dummy

        self.display: List[int] = [0] * 20 # Display untuk lexical levels
        self.current_level: int = 0  # Level lexical saat ini

        #counter
        self.tx: int = 0  # Index terakhir di tab
        self.ax: int = 0  # Index terakhir di atab
        self.bx: int = 0  # Index terakhir di btab

        self._init_reserved_idn()
        self._init_global_block()

    def __str__(self):
        # Cetak Symbol Table (Tab) - Skip dummy index 0
        string = []
        string.append("\n>> Symbol Table (Identifier Table):")
        string.append(f"{'Idx':<5} | {'id':<15} | {'Obj':<10} | {'Type':<10} | {'nrm':<5} | {'Lev':<5} | {'Adr':<5} | {'link':<5}")
        string.append("-" * 55)
        for idx, entry in enumerate(self.tab):
            if idx == 0: continue # Skip dummy
            name = entry.identifier
            obj = entry.obj.value if hasattr(entry.obj, 'value') else str(entry.obj)
            typ = entry.type.name if hasattr(entry.type, 'name') else str(entry.type)
            string.append(f"{idx:<5} | {name:<15} | {obj:<10} | {typ:<10} | {entry.nrm:<5} | {entry.lev:<5} | {entry.adr:<5} | {entry.link:<5}")

        # Cetak Block Table (BTab)
        string.append("\n>> Block Table (Scope Info):")
        for idx, entry in enumerate(self.btab):
            if idx == 0: continue # Skip dummy global wrapper if needed
            string.append(f"{idx} | {entry.last} | {entry.lpar} | {entry.psze} | {entry.vsze} |")
        
        # Cetak Array Table (ATab)
        string.append("\n>> Array Table:" )
        if len(self.atab) == 0:
            string.append("  (empty)")

        for idx, entry in enumerate(self.atab):
            string.append(f"Array {idx}: {entry}")
        
        return "\n".join(string)

    def _init_reserved_idn(self):
        """Inisialisasi reserved identifiers ke dalam symbol table"""
        # Reserved keywords
        reserved_keywords = [
            "PROGRAM", "KONSTAN", "TIPE", "VARIABEL", "PROSEDUR", "FUNGSI",
            "MULAI", "SELESAI", "JIKA", "MAKA", "SELAIN-ITU", "UNTUK",
            "DARI", "KE", "TURUN-KE", "LAKUKAN", "SELAMA", "ULANGI", "SAMPAI",
            "DIV", "MOD", "DAN", "ATAU", "TIDAK"
        ]
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

        # Isi dummy entries untuk reserved keywords (1-24)
        for keyword in reserved_keywords:
            self.tx += 1
            self.tab.append(TabEntry(
                identifier=keyword,
                obj=ObjectKind.CONSTANT,  # Dummy
                type=TypeKind.NOTYPE,
                lev=0, adr=0
            ))

        # Masukkan Tipe
        for name, kind in reserved_types:
            self.enter(name, ObjectKind.TYPE, kind, 0, 1, 0, 0)

        # Masukkan Konstanta
        for name, kind, value in reserved_consts:
            self.enter(name, ObjectKind.CONSTANT, kind, 0, 1, 0, value)

    def _init_global_block(self):
        """Membuat block global (program) di btab[1]"""
        # self.bx += 1
        # self.btab.append(BTabEntry(last=0, lpar=0, psze=0, vsze=0))

        self.display[0] = 0
        
        # Update last di global block agar menunjuk ke reserved words terakhir
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
        self.tx += 1
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
        current_idx = self.tx

        # Update link
        if lev < len(self.display):
            btab_idx = self.display[lev]
            
            # Link entry LAMA ke entry BARU (maju)
            last_idx = self.btab[btab_idx].last
            new_entry.link = last_idx
            
            # Update last pointer
            self.btab[btab_idx].last = current_idx
        return current_idx

    def add_array_type(self, xtyp: TypeKind, etyp: TypeKind, eref: int, low: int, high: int) -> int:
        """
        Mendaftarkan informasi array ke atab.
        Returns: index array di atab
        """
        # 1. Hitung Element Size (elsz)
        elsz = 1
        if etyp == TypeKind.INTEGER or etyp == TypeKind.BOOLEAN or etyp == TypeKind.CHAR:
            elsz = 1
        elif etyp == TypeKind.REAL:
            elsz = 1 # Asumsi 1 unit stack, sesuaikan jika real butuh lebih
        elif etyp == TypeKind.ARRAY:
            # Jika elemennya array, ambil size dari atab referensi (eref)
            # eref is 1-based index to atab
            if eref > 0 and eref < len(self.atab):
                elsz = self.atab[eref].size
        
        # 2. Hitung Total Size
        # Size = jumlah elemen * ukuran per elemen
        count = high - low + 1
        total_size = count * elsz

        # 3. Masukkan ke atab
        self.ax += 1
        new_entry = ATabEntry(
            xtyp=xtyp,
            etyp=etyp,
            eref=eref,
            low=low,
            high=high,
            elsz=elsz,
            size=total_size
        )
        self.atab.append(new_entry)
        
        return self.ax
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

        # Pastikan btab_idx valid
        if current_btab_idx >= len(self.btab):
            # print(f"[DEBUG] Invalid btab index: {current_btab_idx}, len={len(self.btab)}")
            raise ValueError(f"Invalid block table index: {current_btab_idx}")
    
        size = 1
        if type_kind == TypeKind.ARRAY:
            if ref > 0 and ref < len(self.atab):
                size = self.atab[ref].size
            else:
                size = 0

        current_adr = self.btab[current_btab_idx].vsze
        idx = self.enter(
            name=name,
            obj=ObjectKind.VARIABLE,
            type_kind=type_kind,
            ref=ref,
            nrm=1,
            lev=self.current_level,
            adr=current_adr
        )

        # Update ukuran variabel lokal di block ini
        self.btab[current_btab_idx].vsze += size
        return idx

    def add_constant(self, name: str, type_kind: TypeKind, value: Any):
        """Deklarasi Konstanta"""
        # Cek duplikasi DI SCOPE LOKAL
        existing_idx = self.lookup_local(name)
        if existing_idx != 0:
            print(f"[DEBUG] Constant '{name}' already exists at index {existing_idx}")
            raise ValueError(f"Duplicate identifier '{name}' in the same scope.")
    
        idx = self.enter(
            name=name,
            obj=ObjectKind.CONSTANT,
            type_kind=type_kind,
            ref=0,
            nrm=1,
            lev=self.current_level,
            adr=value  # Simpan nilai konstanta di adr
        )
        return idx
    
    def enter_scope(self, scope_name: str):
        """
        Masuk ke scope baru (Procedure/Function).
        Membuat entry baru di btab dan update display.
        """
        self.current_level += 1

        # Buat entry block baru
        self.bx += 1
        self.btab.append(BTabEntry(last=0, lpar=0, psze=0, vsze=0))

        # Update display
        if self.current_level >= len(self.display):
            self.display.extend([0] * (self.current_level - len(self.display) + 1))
    
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
        if btab_idx >= len(self.btab):
            return 0
    
        curr = self.btab[btab_idx].last
        while curr > 0 and curr < len(self.tab):
            entry = self.tab[curr]
            # IMPORTANT: Case-sensitive comparison
            if entry.identifier == name:  # Jangan pakai .upper()
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