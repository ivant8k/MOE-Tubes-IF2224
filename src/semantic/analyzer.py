from typing import Optional
from .ast_nodes import *
from .symbol_table import SymbolTable, ObjectKind, TypeKind, TabEntry

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()

    def visit(self, node: ASTNode):
        """Dispatcher utama untuk mengunjungi node AST."""
        if node is None: 
            return None
        
        # Panggil method visit_NamaNode
        method_name = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        """Fallback untuk node yang belum ada handler spesifiknya."""
        return None

    # =========================================================================
    # PROGRAM & BLOCKS
    # =========================================================================

    def visit_ProgramNode(self, node: ProgramNode):
        # 1. Masukkan nama program ke scope global
        self.symbol_table.enter(
            name=node.name, 
            obj=ObjectKind.PROGRAM, 
            type_kind=TypeKind.NOTYPE, 
            ref=0, nrm=1, lev=0, adr=0
        )

        # 2. Visit Declarations
        for decl in node.declarations:
            self.visit(decl)
            
        # 3. Visit Main Block
        self.visit(node.block)

    # =========================================================================
    # DECLARATIONS
    # =========================================================================
    
    def visit_VarDeclNode(self, node: VarDeclNode):
        # Cek apakah tipe-nya adalah ArrayTypeNode (definisi array langsung)
        if isinstance(node.type_node, ArrayTypeNode):
            # Resolve struktur array dan dapatkan referensi ke atab
            type_kind, ref_idx = self._resolve_array_type(node.type_node)
        else:
            # Tipe primitive atau named type
            type_name = node.type_node.type_name if hasattr(node.type_node, 'type_name') else str(node.type_node)
            type_kind = self._resolve_type_str(type_name)
            ref_idx = 0 
            # Note: Jika named type merujuk ke array (TYPE A = ARRAY...), 
            # ref_idx harus diambil dari lookup identifier tipe tersebut.
            if type_kind == TypeKind.NOTYPE:
                # Coba lookup apakah ini Tipe Bentukan (Named Type)
                type_entry_idx = self.symbol_table.lookup(type_name)
                if type_entry_idx != 0:
                    entry = self.symbol_table.get_entry(type_entry_idx)
                    if entry.obj == ObjectKind.TYPE:
                        type_kind = entry.type
                        ref_idx = entry.ref

        try:
            # add_variable sekarang menerima ref (penting untuk array)
            idx = self.symbol_table.add_variable(node.var_name, type_kind, ref=ref_idx)
            
            if idx is None:
                print(f"[Semantic Error] Failed to add variable '{node.var_name}'")
                return

            entry = self.symbol_table.get_entry(idx)
            node.type = entry.type.name
            node.symbol_entry = {'tab_index': idx, 'lev': entry.lev}
            
        except ValueError as e:
            print(f"[Semantic Error] {e}")

    def _resolve_array_type(self, node: ArrayTypeNode):
        """
        Memproses ArrayTypeNode, mendaftarkan ke atab, dan mengembalikan (TypeKind.ARRAY, ref_index)
        """
        # 1. Evaluate Bounds (Low & High)
        # Asumsi bounds harus constant expression
        low_val = self._get_constant_value(node.lower)
        high_val = self._get_constant_value(node.upper)
        
        if low_val is None or high_val is None:
            print("[Semantic Error] Array bounds must be constant integers.")
            return TypeKind.NOTYPE, 0

        if low_val > high_val:
            print(f"[Semantic Error] Array lower bound ({low_val}) > upper bound ({high_val})")

        # 2. Resolve Element Type
        # Element bisa berupa simple type atau ArrayTypeNode lain (Multidimensional)
        if isinstance(node.element_type, ArrayTypeNode):
            etyp, eref = self._resolve_array_type(node.element_type)
        else:
            # Simple Type / Named Type
            type_name = getattr(node.element_type, 'type_name', str(node.element_type))
            etyp = self._resolve_type_str(type_name)
            eref = 0
            
            # Handle Named Type untuk element
            if etyp == TypeKind.NOTYPE:
                 type_entry_idx = self.symbol_table.lookup(type_name)
                 if type_entry_idx != 0:
                    entry = self.symbol_table.get_entry(type_entry_idx)
                    if entry.obj == ObjectKind.TYPE:
                        etyp = entry.type
                        eref = entry.ref

        # 3. Register to ATAB
        # Tipe index default INTEGER (bisa dikembangkan jika support char/enum index)
        xtyp = TypeKind.INTEGER 
        
        atab_idx = self.symbol_table.add_array_type(xtyp, etyp, eref, low_val, high_val)
        
        return TypeKind.ARRAY, atab_idx

    def _get_constant_value(self, node: ASTNode) -> Optional[int]:
        """Helper untuk mengevaluasi nilai konstan statis dari AST Node"""
        if isinstance(node, NumNode):
            return int(node.value)
        
        if isinstance(node, UnaryOpNode):
            val = self._get_constant_value(node.expr)
            if val is not None:
                if node.op == '-': return -val
                if node.op == '+': return val
        
        if isinstance(node, VarNode):
            # Lookup const identifier
            idx = self.symbol_table.lookup(node.name)
            if idx != 0:
                entry = self.symbol_table.get_entry(idx)
                if entry.obj == ObjectKind.CONSTANT:
                    return int(entry.adr) # Nilai konstanta disimpan di adr
        
        # NOTE: Bisa dikembangkan untuk handle BinOp (misal: 10 + 5)
        return None

    def visit_ConstDeclNode(self, node: ConstDeclNode):
        # 1. Evaluasi Tipe Nilai
        value_type = self.visit(node.value) # Mengembalikan TypeKind
        
        # 2. Ambil Nilai Raw (untuk disimpan di adr)
        raw_value = 0
        if hasattr(node.value, 'value'):
            raw_value = node.value.value

        try:
            idx = self.symbol_table.add_constant(node.const_name, value_type, raw_value)
            
            # ← TAMBAHKAN SAFETY CHECK
            if idx is None:
                print(f"[Semantic Error] Failed to add constant '{node.const_name}'")
                return
            
            # Dekorasi node (opsional)
            entry = self.symbol_table.get_entry(idx)
            if entry:
                node.type = entry.type.name
                node.symbol_entry = {'tab_index': idx, 'lev': entry.lev}
                
        except ValueError as e:
            print(f"[Semantic Error] {e}")

    def visit_TypeDeclNode(self, node: TypeDeclNode):
        # Untuk Milestone 3 dasar, kita catat namanya saja
        # Pengembangan lanjut: simpan struktur array/record di atab/btab
        type_kind = TypeKind.NOTYPE
        ref_idx = 0
        
        # 1. Cek apakah value-nya adalah Definisi Array
        if isinstance(node.value, ArrayTypeNode):
            # Reuse logic _resolve_array_type yang sudah ada
            type_kind, ref_idx = self._resolve_array_type(node.value)
            
        # 2. Cek apakah value-nya adalah Tipe Lain (Alias, misal: TYPE Angka = Integer)
        elif isinstance(node.value, TypeNode):
            type_kind = self._resolve_type_str(node.value.type_name)
            # Jika alias ke array yang sudah ada, perlu lookup ref-nya (opsional/advanced)
            
        try:
            # Masukkan ke Symbol Table sebagai ObjectKind.TYPE
            self.symbol_table.enter(
                node.type_name, 
                ObjectKind.TYPE, 
                type_kind, 
                ref_idx, # Simpan referensi ke atab
                1, 
                self.symbol_table.current_level, 
                0
            )
        except Exception as e:
            print(f"[Semantic Error] {e}")
    # =========================================================================
    # SUBPROGRAMS (Procedure & Function)
    # =========================================================================

    def visit_ProcedureDeclNode(self, node: ProcedureDeclNode):
        proc_name = node.name
        
        # 1. Daftarkan Prosedur di Scope Parent
        self.symbol_table.enter(
            proc_name, 
            ObjectKind.PROCEDURE, 
            TypeKind.NOTYPE, 
            0, 1, self.symbol_table.current_level, 0
        )

        # 2. Masuk Scope Baru
        self.symbol_table.enter_scope(proc_name)
        
        # 3. Proses Parameter
        for param in node.params:
            self.visit_ParameterNode(param)

        current_btab = self.symbol_table.btab[self.symbol_table.display[self.symbol_table.current_level]]
        current_btab.lpar = self.symbol_table.tx

        if hasattr(node, 'local_vars'):
            for decl in node.local_vars:
                self.visit(decl)
         # 4. Proses Block (yang sudah include deklarasi lokal & statements)
        if node.block:
            self.visit(node.block)
        
        # 5. Keluar Scope
        self.symbol_table.exit_scope()

    def visit_FunctionDeclNode(self, node: FunctionDeclNode):
        func_name = node.name
        return_type = self._resolve_type_str(node.return_type.type_name)
        
        # 1. Daftarkan Fungsi di Scope Parent (dengan tipe kembalian)
        self.symbol_table.enter(
            func_name, 
            ObjectKind.FUNCTION, 
            return_type, 
            0, 1, self.symbol_table.current_level, 0
        )

        # 2. Masuk Scope Baru
        self.symbol_table.enter_scope(func_name)
        
        # 3. Parameter
        for param in node.params:
            self.visit_ParameterNode(param)

        if hasattr(node, 'local_vars'):
            for decl in node.local_vars:
                self.visit(decl)
            
        # 4. Proses Block (yang sudah include deklarasi & body)
        if node.block:
            self.visit(node.block)
        
        # 5. Keluar Scope
        self.symbol_table.exit_scope()

    def visit_ParameterNode(self, node: ParameterNode):
        type_kind = self._resolve_type_str(node.type_node.type_name)
        for name in node.names:
            try:
                # Masukkan parameter sebagai variabel lokal
                # Note: node.is_ref (VAR param) bisa disimpan di field nrm (0=ref, 1=normal)
                nrm_val = 0 if node.is_ref else 1
                
                # Kita pakai enter manual karena add_variable default nrm=1
                # Hitung offset (adr) manual jika perlu, atau pakai logic add_variable
                self.symbol_table.enter(
                    name, ObjectKind.VARIABLE, type_kind, 0, nrm_val, 
                    self.symbol_table.current_level, 0
                )
            except ValueError as e:
                print(f"[Semantic Error] {e}")

    # =========================================================================
    # STATEMENTS
    # =========================================================================

    def visit_CompoundNode(self, node: CompoundNode):
        for child in node.children:
            self.visit(child)

    def visit_AssignNode(self, node: AssignNode):
        # 1. Cek Tipe Target (Variable)
        target_type = self.visit(node.target)
        
        # 2. Cek Tipe Value (Expression)
        value_type = self.visit(node.value)
        if target_type is None: target_type = TypeKind.NOTYPE
        if value_type is None: value_type = TypeKind.NOTYPE        
        # 3. Validasi Kompatibilitas
        if target_type != value_type and target_type != TypeKind.NOTYPE and value_type != TypeKind.NOTYPE:
            # Implicit casting: Integer -> Real (OK)
            if target_type == TypeKind.REAL and value_type == TypeKind.INTEGER:
                return
            
            print(f"[Semantic Error] Type mismatch in assignment. "
                  f"Cannot assign {value_type.name} to {target_type.name}")

    def visit_IfNode(self, node: IfNode):
        cond_type = self.visit(node.condition)
        if cond_type != TypeKind.BOOLEAN and cond_type != TypeKind.NOTYPE:
            print(f"[Semantic Error] IF condition must be BOOLEAN, got {cond_type.name}")
        
        self.visit(node.true_block)
        if node.else_block:
            self.visit(node.else_block)

    def visit_WhileNode(self, node: WhileNode):
        cond_type = self.visit(node.condition)
        if cond_type != TypeKind.BOOLEAN and cond_type != TypeKind.NOTYPE:
            print(f"[Semantic Error] WHILE condition must be BOOLEAN, got {cond_type.name}")
        self.visit(node.body)

    def visit_ForNode(self, node: ForNode):
        # Cek variabel loop
        var_idx = self.symbol_table.lookup(node.variable)
        if var_idx == 0:
            print(f"[Semantic Error] Loop variable '{node.variable}' not declared.")
        
        # Cek tipe expression start & end (harus integer)
        start_type = self.visit(node.start_expr)
        end_type = self.visit(node.end_expr)
        
        if start_type != TypeKind.INTEGER or end_type != TypeKind.INTEGER:
            print("[Semantic Error] FOR loop limits must be INTEGER.")
            
        self.visit(node.body)

    def visit_ProcedureCallNode(self, node: ProcedureCallNode):
        # Handle Built-in functions
        if node.proc_name in ['writeln', 'write', 'readln', 'read']:
            for arg in node.arguments:
                self.visit(arg)
            return

        # Lookup Prosedur/Fungsi
        idx = self.symbol_table.lookup(node.proc_name)
        if idx == 0:
            print(f"[Semantic Error] Identifier '{node.proc_name}' not declared.")
            return TypeKind.NOTYPE
        
        entry = self.symbol_table.get_entry(idx)
        
        # Validasi: Harus Prosedur atau Fungsi
        if entry.obj == ObjectKind.FUNCTION:
            return entry.type
        return TypeKind.NOTYPE

    # =========================================================================
    # EXPRESSIONS & FACTORS
    # =========================================================================
    
    def visit_ArrayAccessNode(self, node: ArrayAccessNode) -> TypeKind:
        # 1. Periksa Variabel Array
        # visit_VarNode akan mengembalikan tipe arraynya dan menempelkan symbol_entry
        array_type = self.visit(node.array)
        
        if array_type != TypeKind.ARRAY:
            print(f"[Semantic Error] Variable is not an array.")
            return TypeKind.NOTYPE

        # 2. Periksa Index
        index_type = self.visit(node.index)
        if index_type != TypeKind.INTEGER:
            print(f"[Semantic Error] Array index must be INTEGER, got {index_type.name}")

        # 3. Ambil Tipe Elemen dari Symbol Table (atab)
        # Kita butuh ref dari node.array (yang sudah dipasang oleh visit_VarNode)
        if not hasattr(node.array, 'symbol_entry'):
            return TypeKind.NOTYPE

        # Ambil referensi ke atab
        tab_idx = node.array.symbol_entry.get('tab_index')
        entry = self.symbol_table.get_entry(tab_idx)
        
        if entry and entry.ref > 0:
            atab_entry = self.symbol_table.atab[entry.ref]
            
            # Validasi Range Index (Hanya bisa jika index berupa angka literal)
            if isinstance(node.index, NumNode):
                val = int(node.index.value)
                if val < atab_entry.low or val > atab_entry.high:
                    print(f"[Semantic Error] Array index out of bounds: {val}. Valid: [{atab_entry.low}..{atab_entry.high}]")

            # Kembalikan tipe elemen (etyp)
            return atab_entry.etyp
            
        return TypeKind.NOTYPE


    def visit_BinOpNode(self, node: BinOpNode) -> TypeKind:
        left = self.visit(node.left)
        right = self.visit(node.right)
        
        if left == TypeKind.NOTYPE or right == TypeKind.NOTYPE:
            return TypeKind.NOTYPE

        op = node.op.lower()

        # Aritmatika: +, -, *, div, mod
        if op in ['+', '-', '*', 'div', 'mod', 'bagi']:
            # Integer operan
            if left == TypeKind.INTEGER and right == TypeKind.INTEGER:
                if op == '/' or op == 'bagi': return TypeKind.REAL
                return TypeKind.INTEGER
            
            # Real operan
            if left == TypeKind.REAL or right == TypeKind.REAL:
                if op == 'div' or op == 'mod':
                     print(f"[Semantic Error] Operator '{op}' only for INTEGER.")
                     return TypeKind.NOTYPE
                return TypeKind.REAL
                
        # Relasional: =, <>, <, >, <=, >=
        if op in ['=', '<>', '<', '>', '<=', '>=']:
            return TypeKind.BOOLEAN
            
        # Logika: and, or
        if op in ['and', 'or', 'dan', 'atau']:
            if left == TypeKind.BOOLEAN and right == TypeKind.BOOLEAN:
                return TypeKind.BOOLEAN
            else:
                print(f"[Semantic Error] Operator '{op}' requires BOOLEAN operands.")
                
        return TypeKind.NOTYPE

    def visit_UnaryOpNode(self, node: UnaryOpNode) -> TypeKind:
        expr_type = self.visit(node.expr)
        op = node.op.lower()
        
        if op == 'tidak' or op == 'not':
            if expr_type == TypeKind.BOOLEAN: return TypeKind.BOOLEAN
        elif op == '-':
            if expr_type in [TypeKind.INTEGER, TypeKind.REAL]: return expr_type
            
        print(f"[Semantic Error] Invalid unary op '{op}' on {expr_type.name}")
        return TypeKind.NOTYPE

    def visit_VarNode(self, node: VarNode) -> TypeKind:
        # 1. Lookup Identifier
        idx = self.symbol_table.lookup(node.name)
        
        if idx == 0:
            print(f"[Semantic Error] Variable '{node.name}' not declared.")
            return TypeKind.NOTYPE
            
        # 2. Ambil Entry
        entry = self.symbol_table.get_entry(idx)
        
        # 3. Dekorasi AST (Isi info tipe & entry ke Node)
        node.type = entry.type.name
        # Simpan tab_index beserta info entry lainnya
        node.symbol_entry = {
            'tab_index': idx,
            'lev': entry.lev,
            'adr': entry.adr,
            'ref': entry.ref,
            'obj': entry.obj,
            'type': entry.type
        }
        
        return entry.type

    def visit_NumNode(self, node: NumNode) -> TypeKind:
        if isinstance(node.value, float): return TypeKind.REAL
        return TypeKind.INTEGER

    def visit_StringNode(self, node: StringNode) -> TypeKind:
        return TypeKind.STRING

    def visit_BoolNode(self, node: BoolNode) -> TypeKind:
        return TypeKind.BOOLEAN
    
    def visit_CharNode(self, node: CharNode) -> TypeKind:
        return TypeKind.CHAR

    def visit_NoOpNode(self, node: NoOpNode):
        return TypeKind.NOTYPE

    # --- HELPERS ---
    def _resolve_type_str(self, type_name: str) -> TypeKind:
        tn = type_name.upper()
        if tn == 'INTEGER': return TypeKind.INTEGER
        if tn == 'REAL': return TypeKind.REAL
        if tn == 'BOOLEAN': return TypeKind.BOOLEAN
        if tn == 'CHAR': return TypeKind.CHAR
        if tn == 'STRING': return TypeKind.STRING
        # Array/Record belum dihandle detail
        if tn == 'ARRAY' or 'ARRAY' in tn: return TypeKind.ARRAY
        return TypeKind.NOTYPE