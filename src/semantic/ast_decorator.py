from .ast_nodes import *
from .analyzer import SemanticAnalyzer
from .symbol_table import TypeKind, ObjectKind

class ASTDecorator(SemanticAnalyzer):
    """
    Decorator untuk menyuntikkan metadata semantik (tab_index, type, lev, dll)
    ke dalam node AST agar siap dicetak.
    """

    def _set_type(self, node: ASTNode, type_kind: TypeKind):
        """Helper untuk set string tipe ke node"""
        if type_kind and type_kind != TypeKind.NOTYPE:
            node.type = type_kind.name  # Misal: 'INTEGER', 'BOOLEAN'
        else:
            node.type = "VOID"

    def _set_void(self, node: ASTNode):
        node.type = "VOID"

    # =========================================================================
    # DECLARATIONS (Update agar VarDecl infonya lengkap & Type pindah ke kanan)
    # =========================================================================

    def visit_VarDeclNode(self, node: VarDeclNode):
        # Jalankan logika asli untuk insert ke Symbol Table
        super().visit_VarDeclNode(node)
        
        # Ambil ulang entry yang baru saja dibuat untuk memastikan data lengkap
        idx = self.symbol_table.lookup_local(node.var_name)
        if idx > 0:
            entry = self.symbol_table.get_entry(idx)
            node.type = entry.type.name # Ini agar muncul di kanan (type:INTEGER)
            
            # Inject info lengkap termasuk ref (a_idx)
            node.symbol_entry = {
                'tab_index': idx,
                'lev': entry.lev,
                'adr': entry.adr,
                'ref': entry.ref # Ini adalah a_index jika tipe array
            }

    # =========================================================================
    # VARIABLES & USAGES (Update agar tab_index muncul)
    # =========================================================================

    def visit_VarNode(self, node: VarNode) -> TypeKind:
        # Jalankan lookup asli
        result_type = super().visit_VarNode(node)
        
        # Cari index-nya secara manual (karena entry.__dict__ tidak punya index)
        idx = self.symbol_table.lookup(node.name)
        
        if idx > 0:
            entry = self.symbol_table.get_entry(idx)
            # Override symbol_entry agar punya tab_index eksplisit
            node.symbol_entry = {
                'tab_index': idx,
                'lev': entry.lev,
                'adr': entry.adr,
                'ref': entry.ref # a_index
            }
        
        return result_type

    # =========================================================================
    # PROGRAM & BLOCKS
    # =========================================================================

    def visit_ProgramNode(self, node: ProgramNode):
        super().visit_ProgramNode(node)
        node.type = "PROGRAM"
        node.symbol_entry = {'lev': 0}

    def visit_CompoundNode(self, node: CompoundNode):
        # Simpan state sebelum visit children
        current_lev = self.symbol_table.current_level
        current_block_idx = self.symbol_table.bx

        node.type = "BLOCK"
        node.symbol_entry = {
            'block_index': current_block_idx, # b_index
            'lev': current_lev
        }
        super().visit_CompoundNode(node)

    # =========================================================================
    # EXPRESSIONS & STATEMENTS
    # =========================================================================

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
        super().visit_ProcedureCallNode(node)
        if node.proc_name in ['writeln', 'write', 'readln', 'read']:
             node.type = "PREDEFINED"
        else:
            self._set_void(node)
            idx = self.symbol_table.lookup(node.proc_name)
            if idx > 0:
                entry = self.symbol_table.get_entry(idx)
                node.symbol_entry = {'tab_index': idx, 'lev': entry.lev}

    def generate_decorated_ast(self, root_node: ASTNode) -> ASTNode:
        self.visit(root_node)
        return root_node