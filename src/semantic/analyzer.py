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
        # 1. Resolve Tipe Data dari String ke Enum
        type_name = node.type_node.type_name
        type_kind = self._resolve_type_str(type_name)
        
        if type_kind == TypeKind.NOTYPE:
            # Cek apakah ini tipe bentukan user (Array/Record)
            # TODO: Implementasi lookup tipe kustom di sini
            pass

        # 2. Masukkan ke Symbol Table
        try:
            # add_variable mengembalikan index
            idx = self.symbol_table.add_variable(node.var_name, type_kind)
            
            if idx is None:
                print(f"[Semantic Error] Failed to add variable '{node.var_name}'")
                return

            # Dekorasi AST Node
            entry = self.symbol_table.get_entry(idx)
            node.type = entry.type.name
            node.symbol_entry = {
                'tab_index': idx,
                'lev': entry.lev
            }
            
        except ValueError as e:
            print(f"[Semantic Error] {e}")

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
        try:
            self.symbol_table.enter(
                node.type_name, 
                ObjectKind.TYPE, 
                TypeKind.NOTYPE, # Atau TypeKind.ARRAY jika array
                0, 1, self.symbol_table.current_level, 0
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

        # Lookup Prosedur
        idx = self.symbol_table.lookup(node.proc_name)
        if idx == 0:
            print(f"[Semantic Error] Procedure '{node.proc_name}' not declared.")
        else:
            entry = self.symbol_table.get_entry(idx)
            if entry.obj != ObjectKind.PROCEDURE:
                 print(f"[Semantic Error] '{node.proc_name}' is not a procedure.")
            # TODO: Cek jumlah parameter (entry.ref ke btab, lalu cek psze/count)

    # =========================================================================
    # EXPRESSIONS & FACTORS
    # =========================================================================

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
        node.symbol_entry = entry.__dict__ # Simpan dictionary entry
        
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