from .ast_nodes import *
from .ast_analyzer import ASTAnalyzer
from .symbol_table import SymbolTable, TypeKind, ObjectKind, TabEntry

# =========================================================================
# 1. PATCHED SYMBOL TABLE (Pertahankan perbaikan Link Mundur)
# =========================================================================
class PatchedSymbolTable(SymbolTable):
    def enter(self, name:str, obj:ObjectKind, type_kind:TypeKind, ref:int, nrm:int, lev:int, adr:int) -> int:
        previous_idx = 0
        btab_idx = 0
        if lev < len(self.display):
            btab_idx = self.display[lev]
            previous_idx = self.btab[btab_idx].last

        current_idx = super().enter(name, obj, type_kind, ref, nrm, lev, adr)
        self.tab[current_idx].link = previous_idx # Backward link fix
        return current_idx

# =========================================================================
# 2. AST DECORATOR
# =========================================================================
class ASTDecorator(ASTAnalyzer):
    
    def __init__(self):
        super().__init__()
        # Gunakan tabel yang sudah dipatch
        self.symbol_table = PatchedSymbolTable()

    def _set_type(self, node: ASTNode, type_kind: TypeKind):
        if type_kind and type_kind != TypeKind.NOTYPE:
            node.type = type_kind.name 
        else:
            node.type = "VOID"

    def _set_void(self, node: ASTNode):
        node.type = "VOID"

    # =========================================================================
    # DECLARATIONS & PARAMETERS (NEW: Handle ParameterNode)
    # =========================================================================

    def visit_VarDeclNode(self, node: VarDeclNode):
        super().visit_VarDeclNode(node)
        idx = self.symbol_table.lookup_local(node.var_name)
        if idx > 0:
            entry = self.symbol_table.get_entry(idx)
            node.type = entry.type.name
            node.symbol_entry = {
                'tab_index': idx, 'lev': entry.lev, 
                'adr': entry.adr, 'ref': entry.ref
            }

    def visit_ParameterNode(self, node: ParameterNode):
        # 1. Jalankan logic asli (insert ke tabel simbol)
        super().visit_ParameterNode(node)
        
        # 2. Decorate
        # ASTConverter membuat ParameterNode per satu nama, jadi kita ambil names[0]
        if node.names:
            name = node.names[0]
            # Lookup local karena parameter ada di scope prosedur itu sendiri
            idx = self.symbol_table.lookup_local(name)
            if idx > 0:
                entry = self.symbol_table.get_entry(idx)
                node.type = entry.type.name
                node.symbol_entry = {
                    'tab_index': idx,
                    'lev': entry.lev,
                    'adr': entry.adr,
                    'ref': entry.ref
                }

    # =========================================================================
    # PROGRAM & BLOCKS
    # =========================================================================

    def visit_ProgramNode(self, node: ProgramNode):
        super().visit_ProgramNode(node)
        node.type = "PROGRAM"
        node.symbol_entry = {'lev': 0}

    def visit_CompoundNode(self, node: CompoundNode):
        current_lev = self.symbol_table.current_level
        current_block_idx = self.symbol_table.bx
        node.type = "BLOCK"
        node.symbol_entry = {'block_index': current_block_idx, 'lev': current_lev}
        super().visit_CompoundNode(node)

    # =========================================================================
    # VARIABLES & OPERATIONS
    # =========================================================================

    def visit_VarNode(self, node: VarNode) -> TypeKind:
        result_type = super().visit_VarNode(node)
        idx = self.symbol_table.lookup(node.name)
        if idx > 0:
            entry = self.symbol_table.get_entry(idx)
            node.symbol_entry = {
                'tab_index': idx, 'lev': entry.lev, 
                'adr': entry.adr, 'ref': entry.ref
            }
        return result_type

    def visit_BinOpNode(self, node: BinOpNode) -> TypeKind:
        result_type = super().visit_BinOpNode(node)
        self._set_type(node, result_type)
        return result_type

    def visit_UnaryOpNode(self, node: UnaryOpNode) -> TypeKind:
        result_type = super().visit_UnaryOpNode(node)
        self._set_type(node, result_type)
        return result_type

    def visit_NumNode(self, node: NumNode) -> TypeKind:
        result_type = super().visit_NumNode(node)
        self._set_type(node, result_type)
        return result_type

    # =========================================================================
    # STATEMENTS (Updated: ProcedureCall visit arguments)
    # =========================================================================

    def visit_AssignNode(self, node: AssignNode):
        super().visit_AssignNode(node)
        self._set_void(node)

    def visit_IfNode(self, node: IfNode):
        super().visit_IfNode(node)
        node.type = "STATEMENT"
    
    def visit_ForNode(self, node: ForNode):
        super().visit_ForNode(node)
        node.type = "STATEMENT"

    def visit_WhileNode(self, node: WhileNode):
        super().visit_WhileNode(node)
        node.type = "STATEMENT"

    def visit_ProcedureCallNode(self, node: ProcedureCallNode):
        # Jalankan logic asli (lookup nama prosedur)
        super().visit_ProcedureCallNode(node)
        
        if node.proc_name in ['writeln', 'write', 'readln', 'read']:
             node.type = "PREDEFINED"
        else:
            # Handle User Defined Procedure
            idx = self.symbol_table.lookup(node.proc_name)
            if idx > 0:
                entry = self.symbol_table.get_entry(idx)
                node.symbol_entry = {'tab_index': idx, 'lev': entry.lev}
                if entry.obj == ObjectKind.FUNCTION:
                    node.type = entry.type.name
                else:
                    self._set_void(node)
            
            # [FIX] Force visit arguments agar VarNode di dalamnya ter-dekorasi
            # Analyzer asli kadang skip visit argumen user-defined procedure
            for arg in node.arguments:
                self.visit(arg)

    def generate_decorated_ast(self, root_node: ASTNode) -> ASTNode:
        self.visit(root_node)
        return root_node