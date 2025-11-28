from .ast_nodes import *

class ASTPrinter:
    def print(self, node):
        """Entry point untuk mencetak AST"""
        return self._print_node(node, "", True)

    def _print_node(self, node, prefix, is_last):
        # 1. Dapatkan Label Node (Text Header)
        label = self._get_label(node)
        annot = self._get_annotation(node)
        
        connector = "\\-- " if is_last else "+-- "
        if prefix == "": result = f"{label}{annot}\n"
        else: result = f"{prefix}{connector}{label}{annot}\n"

        # 2. Dapatkan Children (Virtual atau Real)
        children_map = self._get_children(node)
        
        # 3. Print Children
        child_prefix = prefix + ("    " if is_last else "|   ")
        count = len(children_map)
        
        for i, (tag, child) in enumerate(children_map):
            is_last_child = (i == count - 1)
            
            if tag: # Virtual Node (Declarations / Block)
                tag_conn = "\\-- " if is_last_child else "+-- "
                result += f"{child_prefix}{tag_conn}{tag}\n"
                virtual_prefix = child_prefix + ("    " if is_last_child else "|   ")
                
                # Logic Unwrap untuk Block -> CompoundNode
                items = []
                if (tag in ["Block", "Body"]) and isinstance(child, CompoundNode):
                    items = child.children
                elif isinstance(child, list):
                    items = child
                elif isinstance(child, ASTNode):
                    items = [child]

                for k, item in enumerate(items):
                    is_last_item = (k == len(items) - 1)
                    # Rekursi
                    result += self._print_node(item, virtual_prefix, is_last_item)
            else:
                # Direct Child
                result += self._print_node(child, child_prefix, is_last_child)
                
        return result

    # --- HELPERS ---

    def _get_annotation(self, node) -> str:
        parts = []
        # Cek keberadaan atribut sebelum akses
        if hasattr(node, 'symbol_entry') and node.symbol_entry and 'tab_index' in node.symbol_entry:
            parts.append(f"idx:{node.symbol_entry['tab_index']}")
        if hasattr(node, 'type') and node.type:
            parts.append(f"type:{node.type.lower()}")
        return " \t→ " + ", ".join(parts) if parts else ""

    def _get_label(self, node) -> str:
        """Menentukan teks yang muncul di node"""
        if isinstance(node, ProgramNode): return f"Program('{node.name}')"
        
        if isinstance(node, VarDeclNode):
            t_name = getattr(node.type_node, 'type_name', 'unknown')
            return f"VarDecl(name: '{node.var_name}', type: '{t_name}')"
        
        if isinstance(node, ConstDeclNode): return f"ConstDecl('{node.const_name}')"
        if isinstance(node, TypeDeclNode): return f"TypeDecl('{node.type_name}')"
        if isinstance(node, TypeNode): return f"Type('{node.type_name}')"
        
        if isinstance(node, ProcedureCallNode):
            args = [self._compact(a) for a in node.arguments]
            return f"ProcedureCall(name: '{node.proc_name}', args: [{', '.join(args)}])"
        
        if isinstance(node, AssignNode):
            val_str = self._compact(node.value)
            target_str = self._compact(node.target) or "Target"
            if val_str: return f"Assign(target: {target_str}, value: {val_str})"
            return f"Assign"

        if isinstance(node, BinOpNode): return f"BinOp('{node.op}')"
        if isinstance(node, UnaryOpNode): return f"UnaryOp('{node.op}')"
        if isinstance(node, VarNode): return f"Var('{node.name}')"
        if isinstance(node, NumNode): return f"Num({node.value})"
        if isinstance(node, StringNode): return f"String('{node.value}')"
        
        if isinstance(node, ParameterNode):
            prefix = "VAR " if node.is_ref else ""
            t = getattr(node.type_node, 'type_name', '?')
            return f"Param({prefix}{','.join(node.names)}: {t})"
        
        if isinstance(node, ProcedureDeclNode): return f"ProcedureDecl('{node.name}')"
        if isinstance(node, FunctionDeclNode): return f"FunctionDecl('{node.name}')"
        if isinstance(node, ForNode): return f"For('{node.variable}')"

        return node.__class__.__name__.replace("Node", "")

    def _compact(self, node):
        if isinstance(node, VarNode): return f"Var('{node.name}')"
        if isinstance(node, NumNode): return f"Num({node.value})"
        if isinstance(node, StringNode): return f"String('{node.value}')"
        return None

    def _get_children(self, node):
        """Menentukan anak mana yang akan dicetak dan grouping-nya"""
        children = []
        
        if isinstance(node, ProgramNode):
            if node.declarations: children.append(("Declarations", node.declarations))
            children.append(("Block", node.block))
            return children

        # FIX: Gunakan getattr(node, 'attr', None) untuk menghindari AttributeError
        # jika field belum ada di definisi ASTNode lama
        if isinstance(node, (ProcedureDeclNode, FunctionDeclNode)):
            params = getattr(node, 'params', [])
            decls = getattr(node, 'declarations', []) # Safe access
            body = getattr(node, 'body', None) or getattr(node, 'block', None) # Support old & new field name

            if params: children.append(("Params", params))
            if decls: children.append(("Declarations", decls))
            if body: children.append(("Body", body))
            return children

        if isinstance(node, AssignNode):
            if self._compact(node.value): return []
            if not self._compact(node.target): children.append((None, node.target))
            children.append((None, node.value))
        
        elif isinstance(node, BinOpNode):
            children.append((None, node.left))
            children.append((None, node.right))
            
        elif isinstance(node, UnaryOpNode):
            children.append((None, node.expr))
            
        elif isinstance(node, IfNode):
            children.append((None, node.condition))
            children.append((None, node.true_block))
            if node.else_block: children.append((None, node.else_block))
            
        elif isinstance(node, WhileNode):
            children.append((None, node.condition))
            children.append((None, node.body))
            
        elif isinstance(node, ForNode):
            children.append((None, node.start_expr))
            children.append((None, node.end_expr))
            children.append((None, node.body))

        elif isinstance(node, CompoundNode):
            for c in node.children:
                children.append((None, c))

        elif isinstance(node, ArrayAccessNode):
            children.append((None, node.index))

        return children