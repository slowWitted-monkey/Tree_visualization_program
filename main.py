"""Trail Tree Explorer: a visual, interactive introduction to binary trees.

Run with Python 3.10+:
    python main.py

Uses only Python's standard library (Tkinter).
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import tkinter as tk
from tkinter import messagebox, ttk


PAPER = "#f4efe5"
INK = "#253039"
MUTED = "#65737a"
CANVAS = "#18262d"
TEAL = "#4dd0b0"
BLUE = "#72b7ff"
GOLD = "#ffd166"
CORAL = "#ff8a72"
WHITE = "#fffaf0"


@dataclass(eq=False)
class Node:
    label: str
    left: "Node | None" = None
    right: "Node | None" = None
    parent: "Node | None" = None


def attach(parent: Node, child: Node, side: str) -> None:
    setattr(parent, side, child)
    if child is not None:
        child.parent = parent


def preorder(root):
    if root is None:
        return []
    return [root] + preorder(root.left) + preorder(root.right)


def inorder(root):
    if root is None:
        return []
    return inorder(root.left) + [root] + inorder(root.right)


def postorder(root):
    if root is None:
        return []
    return postorder(root.left) + postorder(root.right) + [root]


def level_order(root):
    result = []
    queue = deque([root] if root else [])
    while queue:
        node = queue.popleft()
        result.append(node)
        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)
    return result


def node_depth(node):
    depth = 0
    while node.parent:
        depth += 1
        node = node.parent
    return depth


def node_height(node):
    if node is None:
        return -1
    return 1 + max(node_height(node.left), node_height(node.right))


def leaves(root):
    return [n for n in preorder(root) if n.left is None and n.right is None]


def is_balanced_by_leaves(root):
    depths = [node_depth(n) for n in leaves(root)]
    return bool(depths) and max(depths) - min(depths) <= 1


def is_full_pdf_definition(root):
    if root is None:
        return False
    leaf_depths = [node_depth(n) for n in leaves(root)]
    every_branch_splits = all(
        (n.left is None) == (n.right is None) for n in preorder(root)
    )
    return every_branch_splits and len(set(leaf_depths)) == 1


def is_complete(root):
    if root is None:
        return False
    queue = deque([root])
    found_gap = False
    while queue:
        node = queue.popleft()
        for child in (node.left, node.right):
            if child is None:
                found_gap = True
            else:
                if found_gap:
                    return False
                queue.append(child)
    return True


class TrailTreeExplorer(tk.Tk):
    ORDERS = {
        "Preorder": preorder,
        "Inorder": inorder,
        "Postorder": postorder,
        "Level-order": level_order,
    }
    ORDER_HELP = {
        "Preorder": "Visit the signpost first, then walk its left trail, then its right trail.",
        "Inorder": "Walk the left trail, visit the signpost, then walk the right trail.",
        "Postorder": "Explore both trails before visiting the signpost.",
        "Level-order": "Visit every place at this distance from the start, left to right, before going deeper.",
    }

    def __init__(self):
        super().__init__()
        self.title("Trail Tree Explorer")
        self.geometry("1320x850")
        self.minsize(1050, 700)
        self.configure(bg=PAPER)
        self.root_node = None
        self.selected = None
        self.highlight = None
        self.positions = {}
        self.sequence = []
        self.step_index = 0
        self.timer = None
        self.order = tk.StringVar(value="Preorder")
        self.new_label = tk.StringVar()
        self.explanation = tk.StringVar(value="Start by creating the trailhead (the root).")
        self.status = tk.StringVar(value="A binary tree is a hierarchy where each place has at most two child places.")

        self._build_ui()
        self._load_example()

    def _build_ui(self):
        header = tk.Frame(self, bg=PAPER)
        header.pack(fill="x", padx=24, pady=(18, 12))
        tk.Label(header, text="TRAIL TREE EXPLORER", bg=PAPER, fg=INK,
                 font=("Segoe UI", 23, "bold")).pack(side="left")
        tk.Label(header, text="A hands-on guide to binary trees", bg=PAPER, fg=MUTED,
                 font=("Segoe UI", 11)).pack(side="right")

        body = tk.Frame(self, bg=PAPER)
        body.pack(fill="both", expand=True, padx=22)
        side = tk.Frame(body, bg=PAPER, width=260)
        side.pack(side="left", fill="y", padx=(0, 16))
        side.pack_propagate(False)

        self._heading(side, "Build the trail")
        self._label(side, "New place name")
        entry = tk.Entry(side, textvariable=self.new_label, font=("Segoe UI", 12),
                         relief="solid", bd=1)
        entry.pack(fill="x", ipady=8)
        entry.bind("<Return>", lambda _event: self.add_node())
        self._button(side, "Add as root / child", self.add_node, TEAL)
        self._button(side, "Remove selected branch", self.remove_selected, CORAL)
        self._button(side, "Load example trail", self._load_example, GOLD)
        self._button(side, "Clear trail", self.clear_tree, "#e5ddd0")

        self._heading(side, "Walk the trail")
        self._label(side, "Choose a visit order")
        combo = ttk.Combobox(side, textvariable=self.order,
                             values=list(self.ORDERS), state="readonly")
        combo.pack(fill="x")
        combo.bind("<<ComboboxSelected>>", lambda _event: self.reset_walk())
        walk = tk.Frame(side, bg=PAPER)
        walk.pack(fill="x", pady=8)
        self._button(walk, "Step", self.step, BLUE).pack(side="left", expand=True, fill="x", padx=(0, 3))
        self._button(walk, "Play", self.play, TEAL).pack(side="left", expand=True, fill="x", padx=3)
        self._button(walk, "Reset", self.reset_walk, "#e5ddd0").pack(side="left", expand=True, fill="x", padx=(3, 0))
        self._label(side, "Select a place, then choose which trail to add:")
        row = tk.Frame(side, bg=PAPER)
        row.pack(fill="x")
        self._button(row, "← Left", lambda: self.add_child("left"), BLUE).pack(side="left", expand=True, fill="x", padx=(0, 3))
        self._button(row, "Right →", lambda: self.add_child("right"), BLUE).pack(side="left", expand=True, fill="x", padx=(3, 0))
        tk.Label(side, text="A place can have a left child, a right child, both, or neither.",
                 bg=PAPER, fg=MUTED, font=("Segoe UI", 9), justify="left",
                 wraplength=245).pack(anchor="w", pady=(10, 0))

        main = tk.Frame(body, bg=PAPER)
        main.pack(side="left", fill="both", expand=True)
        bar = tk.Frame(main, bg=PAPER)
        bar.pack(fill="x", pady=(0, 8))
        tk.Label(bar, text="The map", bg=PAPER, fg=INK, font=("Segoe UI", 15, "bold")).pack(side="left")
        self._button(bar, "Fit map", self.draw, "#e5ddd0").pack(side="right")
        self.canvas = tk.Canvas(main, bg=CANVAS, highlightthickness=0, height=390)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda _event: self.draw())
        self.canvas.bind("<Button-1>", self.select_at)

        self.explain_card = tk.Frame(main, bg="#fffaf0", highlightthickness=1, highlightbackground="#d6cec1")
        self.explain_card.pack(fill="x", pady=(10, 0))
        tk.Label(self.explain_card, text="WHAT THIS STEP MEANS", bg="#fffaf0", fg=MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=12, pady=(9, 2))
        tk.Label(self.explain_card, textvariable=self.explanation, bg="#fffaf0", fg=INK,
                 font=("Segoe UI", 11), justify="left", wraplength=900).pack(anchor="w", padx=12, pady=(0, 10))

        footer = tk.Frame(self, bg=PAPER)
        footer.pack(fill="x", padx=24, pady=(10, 14))
        self.facts = tk.StringVar()
        tk.Label(footer, textvariable=self.facts, bg=PAPER, fg=INK,
                 font=("Segoe UI", 10), anchor="w", justify="left").pack(fill="x")
        tk.Label(footer, textvariable=self.status, bg=PAPER, fg=MUTED,
                 font=("Segoe UI", 9), anchor="w").pack(fill="x", pady=(5, 0))
        self._refresh_facts()

    def _heading(self, parent, text):
        tk.Label(parent, text=text, bg=PAPER, fg=INK,
                 font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(14, 7))

    def _label(self, parent, text):
        tk.Label(parent, text=text, bg=PAPER, fg=MUTED,
                 font=("Segoe UI", 10)).pack(anchor="w", pady=(7, 4))

    def _button(self, parent, text, command, color):
        return tk.Button(parent, text=text, command=command, bg=color, fg=INK,
                         activebackground=WHITE, relief="solid", bd=1,
                         cursor="hand2", font=("Segoe UI", 10, "bold"),
                         padx=8, pady=7)

    def add_node(self):
        label = self.new_label.get().strip()
        if not label:
            messagebox.showinfo("Name the place", "Enter a short name for the new place.")
            return
        if len(label) > 18:
            messagebox.showinfo("Shorten the name", "Place names can be up to 18 characters.")
            return
        if self.root_node is None:
            self.root_node = Node(label)
            self.selected = self.root_node
        else:
            if self.selected is None:
                messagebox.showinfo("Select a place", "Click a place on the map first.")
                return
            side = "left" if self.selected.left is None else "right" if self.selected.right is None else None
            if side is None:
                messagebox.showinfo("Both trails are used", "This place already has a left and right child.")
                return
            self._add_child_with_label(self.selected, side, label)
        self.new_label.set("")
        self.reset_walk()
        self._refresh_facts()
        self.draw()

    def add_child(self, side):
        label = self.new_label.get().strip()
        if not label:
            messagebox.showinfo("Name the place", "Enter a short name before adding a child.")
            return
        if len(label) > 18:
            messagebox.showinfo("Shorten the name", "Place names can be up to 18 characters.")
            return
        if self.selected is None:
            messagebox.showinfo("Select a place", "Click a place on the map first.")
            return
        if getattr(self.selected, side) is not None:
            messagebox.showinfo("Trail already exists", f"The {side} trail already leads to a place.")
            return
        self._add_child_with_label(self.selected, side, label)
        self.new_label.set("")
        self.reset_walk()
        self._refresh_facts()
        self.draw()

    def _add_child_with_label(self, parent, side, label):
        child = Node(label)
        attach(parent, child, side)
        self.selected = child
        self.status.set(f"{label} is now the {side} child of {parent.label}.")

    def remove_selected(self):
        if self.selected is None:
            return
        doomed = self.selected
        if doomed.parent is None:
            self.clear_tree()
            return
        parent = doomed.parent
        side = "left" if parent.left is doomed else "right"
        attach(parent, None, side)
        self.selected = parent
        self.reset_walk()
        self._refresh_facts()
        self.draw()
        self.status.set(f"Removed {doomed.label} and its whole subtree from the map.")

    def clear_tree(self):
        self.pause()
        self.root_node = self.selected = self.highlight = None
        self.sequence = []
        self.step_index = 0
        self.status.set("The map is empty. Add a root place to begin.")
        self.explanation.set("The root is the one starting node. It has no parent.")
        self._refresh_facts()
        self.draw()

    def _load_example(self):
        self.pause()
        a, b, c, d, e = [Node(x) for x in ("Trailhead", "Creek", "Lookout", "Bridge", "Cave")]
        attach(a, b, "left")
        attach(a, c, "right")
        attach(b, d, "left")
        attach(b, e, "right")
        self.root_node = a
        self.selected = a
        self.highlight = None
        self.status.set("Example loaded. Click a place to inspect its relationships.")
        self.explanation.set("Trailhead is the root: every route through this map begins here.")
        self.reset_walk()
        self._refresh_facts()
        self.draw()

    def select_at(self, event):
        for node, (x, y) in self.positions.items():
            if (event.x - x) ** 2 + (event.y - y) ** 2 <= 30 ** 2:
                self.selected = node
                self.highlight = None
                self._describe(node)
                self.draw()
                return

    def _describe(self, node):
        depth = node_depth(node)
        parent = node.parent.label if node.parent else "none (this is the root)"
        child_names = [n.label for n in (node.left, node.right) if n]
        if not child_names:
            kind = "leaf"
        else:
            kind = "internal node" if node.parent else "root with children"
        self.explanation.set(
            f"{node.label} is a {kind}. Parent: {parent}. "
            f"Children: {', '.join(child_names) if child_names else 'none'}. "
            f"Level {depth} means {depth} trail edge(s) from the root. "
            f"The highlighted route shows how this place is reached."
        )
        self.status.set(f"Selected {node.label}. Its subtree contains {len(preorder(node))} place(s).")

    def _compute_positions(self):
        nodes = inorder(self.root_node)
        if not nodes:
            return {}
        width = max(self.canvas.winfo_width(), 500)
        height = max(self.canvas.winfo_height(), 300)
        max_depth = max(node_depth(n) for n in nodes)
        gap = min(115, (width - 90) / max(1, len(nodes)))
        start_x = (width - gap * (len(nodes) - 1)) / 2
        top = 64
        vertical = min(112, (height - 120) / max(1, max_depth))
        return {n: (start_x + i * gap, top + node_depth(n) * vertical) for i, n in enumerate(nodes)}

    def draw(self):
        if not hasattr(self, "canvas"):
            return
        c = self.canvas
        c.delete("all")
        width, height = c.winfo_width(), c.winfo_height()
        for x in range(20, width, 38):
            for y in range(20, height, 38):
                c.create_oval(x, y, x + 1, y + 1, fill="#2b3b42", outline="")
        self.positions = self._compute_positions()
        if not self.positions:
            c.create_text(width/2, height/2-12, text="Begin at the trailhead",
                          fill=WHITE, font=("Segoe UI", 20, "bold"))
            c.create_text(width/2, height/2+22, text="Add a root place to create your first node.",
                          fill="#b3c2c5", font=("Segoe UI", 11))
            return
        route = set()
        current = self.highlight
        while current:
            route.add(current)
            current = current.parent
        for node, (x, y) in self.positions.items():
            for side, child in (("left", node.left), ("right", node.right)):
                dx = -1 if side == "left" else 1
                if child:
                    xx, yy = self.positions[child]
                    color = GOLD if node in route and child in route else "#829399"
                    c.create_line(x, y + 25, xx, yy - 27, fill=color, width=3)
                    c.create_text((x + xx) / 2, (y + yy) / 2 - 5, text=side.upper(),
                                  fill="#afc0c1", font=("Segoe UI", 8, "bold"))
                else:
                    # Ghost branch slots make "at most two" visible even when a child is missing.
                    c.create_line(x, y + 23, x + dx * 38, y + 58, fill="#53656a",
                                  width=1, dash=(3, 4))
                    c.create_oval(x + dx * 38 - 3, y + 55, x + dx * 38 + 3, y + 61,
                                  fill="#53656a", outline="")
        for node, (x, y) in self.positions.items():
            color = GOLD if node is self.highlight else TEAL if node is self.selected else BLUE if node is self.root_node else "#31454d"
            c.create_oval(x-30, y-25, x+30, y+25, fill=color, outline=WHITE, width=2)
            c.create_text(x, y, text=node.label, fill=INK, font=("Segoe UI", 9, "bold"),
                          width=52)
            c.create_text(x, y-39, text=("ROOT" if node is self.root_node else
                                         "LEAF" if node.left is None and node.right is None else ""),
                          fill="#c1d0d1", font=("Segoe UI", 8, "bold"))
        c.create_text(14, 15, text=f"{len(self.positions)} PLACES   •   {node_height(self.root_node)} EDGE(S) HIGH",
                      anchor="w", fill="#b3c2c5", font=("Segoe UI", 9, "bold"))

    def reset_walk(self):
        self.pause()
        self.step_index = 0
        self.sequence = self.ORDERS[self.order.get()](self.root_node)
        self.highlight = None
        self.explanation.set(self.ORDER_HELP[self.order.get()])
        self.draw()

    def step(self):
        self.pause()
        if not self.sequence:
            self.status.set("Build a tree before walking its branches.")
            return
        if self.step_index >= len(self.sequence):
            self.step_index = 0
        node = self.sequence[self.step_index]
        self.highlight = node
        self.selected = node
        self.step_index += 1
        done = self.step_index == len(self.sequence)
        self.explanation.set(
            f"{self.ORDER_HELP[self.order.get()]} "
            f"Visit {node.label} now: stop {self.step_index} of {len(self.sequence)}."
        )
        visited = " → ".join(n.label for n in self.sequence[:self.step_index])
        self.status.set(f"{self.order.get()} route so far: {visited}" + ("  •  complete" if done else ""))
        self.draw()

    def play(self):
        if self.timer:
            return
        self.step()
        if self.sequence and self.step_index < len(self.sequence):
            self.timer = self.after(850, self._play_next)

    def _play_next(self):
        self.timer = None
        self.step()
        if self.sequence and self.step_index < len(self.sequence):
            self.timer = self.after(850, self._play_next)

    def pause(self):
        if self.timer:
            self.after_cancel(self.timer)
            self.timer = None

    def _refresh_facts(self):
        root = self.root_node
        if root is None:
            self.facts.set("Nodes: 0   •   Height: —   •   Balanced: —   •   Full: —   •   Complete: —")
            return
        count = len(preorder(root))
        height = node_height(root)
        self.facts.set(
            f"Places: {count}   •   Height: {height} edge(s)   •   "
            f"Balanced: {'yes' if is_balanced_by_leaves(root) else 'no'}   •   "
            f"Full: {'yes' if is_full_pdf_definition(root) else 'no'}   •   "
            f"Complete: {'yes' if is_complete(root) else 'no'}"
        )


if __name__ == "__main__":
    TrailTreeExplorer().mainloop()
