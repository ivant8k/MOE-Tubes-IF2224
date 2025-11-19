from typing import List

from lexical.token import Token

# ===== Class for Parse Tree =====

class NonTerminal(str):
    pass

class Node:
    value: NonTerminal|Token
    children: List["Node"] = []
    
    def __init__(self, value: NonTerminal|Token):
        self.value = value
        self.children: List["Node"] = []

    def addChild(self, node:"Node") -> None:
        self.children.append(node)
    
    def addChildren(self, nodes:List["Node"]) -> None:
        self.children.extend(nodes)

    def __str__(self, level=0, prefix="", is_last=True):
        
        # 1. Tentukan string untuk node ini
        if level == 0:
            # Node root tidak memiliki konektor
            tree_str = f"{self.value}\n"
            child_prefix = "" # Anak dari root tidak punya awalan
        else:
            # Node anak memiliki konektor
            connector = "└── " if is_last else "├── "
            tree_str = f"{prefix}{connector}{self.value}\n"
            
            # Tentukan awalan untuk anak-anak dari node INI
            child_prefix = prefix + ("    " if is_last else "│   ")

        # 2. Rekursif panggil untuk semua anak
        for i, child in enumerate(self.children):
            # Cek apakah anak tersebut adalah anak terakhir
            is_child_last = (i == len(self.children) - 1)
            # Tambahkan representasi string anak ke string tree utama
            tree_str += child.__str__(level + 1, prefix=child_prefix, is_last=is_child_last)
        
        return tree_str