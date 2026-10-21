"""Trail Tree Explorer: build and explore binary trees with Tkinter.

Run with Python 3.10+:
    python main.py
No third-party packages are required.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import math
import tkinter as tk
from tkinter import messagebox, ttk


PAPER = "#f4efe5"
INK = "#253039"
MUTED = "#65737a"
CANVAS = "#1d292f"
TEAL = "#159a7d"
BLUE = "#2999ed"
GOLD = "#e6b836"
CORAL = "#f37360"
PALE = "#fffaf0"
ORDER_COLORS = {
    "Preorder": "#e6b836",
    "Inorder": "#159a7d",
    "Postorder": "#f37360",
    "Level-order": "#2999ed",
}


@dataclass(eq=False)
class Node:
    label: str
    left: "Node | None" = None
    right: "Node | None" = None
    parent: "Node | None" = None


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


def depth(node):
    result = 0
    while node.parent:
        result += 1
        node = node.parent
    return result


def height(node):
    if node is None:
        return -1
    return 1 + max(height(node.left), height(node.right))


def leaf_nodes(root):
    return [n for n in preorder(root) if n.left is None and n.right is None]


def is_balanced(root):
    depths = [depth(n) for n in leaf_nodes(root)]
    return bool(depths) and max(depths) - min(depths) <= 1


def is_full(root):
    if root is None:
        return False
    leaves_at = {depth(n) for n in leaf_nodes(root)}
    every_internal_has_two = all(
        (n.left is None) == (n.right is None) for n in preorder(root)
    )
    return every_internal_has_two and len(leaves_at) == 1


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
            elif found_gap:
                return False
            else:
                queue.append(child)
    return True


def parse_values(text):
    tokens = text.replace(",", " ").split()
    if not tokens:
        raise ValueError("Enter at least one number.")
    if len(tokens) > 63:
        raise ValueError("Use 63 values or fewer so the tree stays readable.")
    values = []
    for token in tokens:
        try:
            value = float(token)
        except ValueError:
            raise ValueError(f"{token!r} is not a number. Separate numeric values with spaces or commas.") from None
        if not math.isfinite(value):
            raise ValueError("Values must be finite numbers.")
        values.append((token, value))
    return values


def build_values(text, arrangement):
    values = parse_values(text)
    nodes = [Node(label) for label, _number in values]
    if arrangement == "Level-filled tree":
        for i, node in enumerate(nodes):
            if 2 * i + 1 < len(nodes):
                node.left = nodes[2 * i + 1]
                node.left.parent = node
            if 2 * i + 2 < len(nodes):
                node.right = nodes[2 * i + 2]
                node.right.parent = node
        return nodes[0]
    root = nodes[0]
    numeric = {node: values[i][1] for i, node in enumerate(nodes)}
    for node in nodes[1:]:
        current = root
        while True:
            side = "left" if numeric[node] < numeric[current] else "right"
            child = getattr(current, side)
            if child is None:
                setattr(current, side, node)
                node.parent = current
                break
            current = child
    return root


class TrailTreeExplorer(tk.Tk):
    TRAVERSALS = {
        "Preorder": preorder,
        "Inorder": inorder,
        "Postorder": postorder,
        "Level-order": level_order,
    }
    WALK_TIPS = {
        "Preorder": "Visit the parent first, then the left subtree, then the right subtree.",
        "Inorder": "Walk the left subtree, visit the parent, then walk the right subtree.",
        "Postorder": "Walk both subtrees before visiting their parent.",
        "Level-order": "Visit one level at a time, from left to right.",
    }

    def __init__(self):
        super().__init__()
        self.title("Trail Tree Explorer")
        self.geometry("1420x900")
        self.minsize(1120, 760)
        self.configure(bg=PAPER)

        self.root_node = None
        self.selected = None
        self.highlight = None
        self.positions = {}
        self.order = tk.StringVar(value="Preorder")
        self.mode = tk.StringVar(value="Build manually")
        self.arrangement = tk.StringVar(value="Binary search tree")
        self.value_text = tk.StringVar()
        self.sequence = []
        self.step_index = 0
        self.timer = None

        self._build_ui()
        self._load_example()

    def _build_ui(self):
        header = tk.Frame(self, bg=PAPER)
        header.pack(fill="x", padx=22, pady=(14, 8))
        tk.Label(header, text="TRAIL TREE EXPLORER", bg=PAPER, fg=INK,
                 font=("Segoe UI", 22, "bold")).pack(side="left")
        tk.Label(header, text="BUILD  /  EXPLORE  /  UNDERSTAND",
                 bg=PAPER, fg=MUTED, font=("Segoe UI", 10)).pack(side="right")

        body = tk.Frame(self, bg=PAPER)
        body.pack(fill="both", expand=True, padx=20, pady=(0, 5))

        side = tk.Frame(body, bg=PAPER, width=275)
        side.pack(side="left", fill="y", padx=(0, 16))
        side.pack_propagate(False)
        main = tk.Frame(body, bg=PAPER)
        main.pack(side="left", fill="both", expand=True)

        self._heading(side, "01  Build your tree")
        self._label(side, "How do you want to build it?")
        mode_box = ttk.Combobox(side, textvariable=self.mode,
                                values=("Build manually", "Build from values"),
                                state="readonly")
        mode_box.pack(fill="x")
        mode_box.bind("<<ComboboxSelected>>", lambda _e: self._show_build_mode())

        self.manual_box = tk.Frame(side, bg=PAPER)
        self._label(self.manual_box, "Name for the new node")
        entry = tk.Entry(self.manual_box, textvariable=self.value_text,
                         font=("Segoe UI", 12), relief="solid", bd=1)
        entry.pack(fill="x", ipady=7)
        entry.bind("<Return>", lambda _e: self.add_root() if self.root_node is None else self.add_child("left"))
        self.selected_label = tk.StringVar(value="Selected node: none")
        tk.Label(self.manual_box, textvariable=self.selected_label, bg=PAPER,
                 fg=MUTED, font=("Segoe UI", 9), anchor="w", wraplength=260,
                 justify="left").pack(fill="x", pady=(7, 4))
        self.root_button = self._button(self.manual_box, "Set as root", self.add_root, BLUE)
        self.root_button.pack(fill="x", pady=3)
        child_row = tk.Frame(self.manual_box, bg=PAPER)
        child_row.pack(fill="x", pady=3)
        self._button(child_row, "Add left child", lambda: self.add_child("left"), TEAL).pack(side="left", expand=True, fill="x", padx=(0, 3))
        self._button(child_row, "Add right child", lambda: self.add_child("right"), TEAL).pack(side="left", expand=True, fill="x", padx=(3, 0))
        self._button(self.manual_box, "Remove selected subtree", self.remove_selected, CORAL).pack(fill="x", pady=3)
        tk.Label(self.manual_box, text="Tip: click a node on the map to choose where the next child goes.",
                 bg=PAPER, fg=MUTED, font=("Segoe UI", 9), wraplength=260,
                 justify="left").pack(anchor="w", pady=(4, 0))

        self.values_box = tk.Frame(side, bg=PAPER)
        self._label(self.values_box, "Numbers (separate with spaces or commas)")
        values_entry = tk.Entry(self.values_box, textvariable=self.value_text,
                                font=("Segoe UI", 11), relief="solid", bd=1)
        values_entry.pack(fill="x", ipady=7)
        values_entry.bind("<Return>", lambda _e: self.build_from_values())
        self._label(self.values_box, "Tree arrangement")
        arrange = ttk.Combobox(self.values_box, textvariable=self.arrangement,
                               values=("Binary search tree", "Level-filled tree"),
                               state="readonly")
        arrange.pack(fill="x")
        tk.Label(self.values_box,
                 text="BST: smaller values go left; equal or larger go right.\nLevel-filled: fill each level left to right.",
                 bg=PAPER, fg=MUTED, font=("Segoe UI", 9), wraplength=260,
                 justify="left").pack(anchor="w", pady=(5, 2))
        self._button(self.values_box, "Build tree", self.build_from_values, BLUE).pack(fill="x", pady=4)

        buttons = tk.Frame(side, bg=PAPER)
        buttons.pack(fill="x", pady=(7, 0))
        self._button(buttons, "Load example", self._load_example, GOLD).pack(side="left", expand=True, fill="x", padx=(0, 3))
        self._button(buttons, "Clear", self.clear_tree, "#e5ddd0").pack(side="left", expand=True, fill="x", padx=(3, 0))

        self._heading(side, "02  Walk the branches")
        self._label(side, "Traversal")
        order_box = ttk.Combobox(side, textvariable=self.order,
                                 values=list(self.TRAVERSALS), state="readonly")
        order_box.pack(fill="x")
        order_box.bind("<<ComboboxSelected>>", lambda _e: self.select_order())
        controls = tk.Frame(side, bg=PAPER)
        controls.pack(fill="x", pady=7)
        self._button(controls, "Step", self.step, BLUE).pack(side="left", expand=True, fill="x", padx=(0, 3))
        self.play_button = self._button(controls, "Play", self.play, TEAL)
        self.play_button.pack(side="left", expand=True, fill="x", padx=3)
        self._button(controls, "Reset", self.reset_walk, "#e5ddd0").pack(side="left", expand=True, fill="x", padx=(3, 0))

        bar = tk.Frame(main, bg=PAPER)
        bar.pack(fill="x", pady=(0, 6))
        tk.Label(bar, text="Tree canvas", bg=PAPER, fg=INK,
                 font=("Segoe UI", 15, "bold")).pack(side="left")
        self._button(bar, "Fit", self.draw, "#e5ddd0").pack(side="right")
        self.canvas = tk.Canvas(main, bg=CANVAS, highlightthickness=1,
                                highlightbackground=INK, height=340)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda _e: self.draw())
        self.canvas.bind("<Button-1>", self.select_at)
        self.node_info = tk.StringVar(value="Click a node to learn about its place in the tree.")
        tk.Label(main, textvariable=self.node_info, bg=PAPER, fg=INK,
                 anchor="w", justify="left", wraplength=1000,
                 font=("Segoe UI", 9)).pack(fill="x", pady=(5, 5))

        tk.Label(main, text="Traversal results  •  click a row to select its order",
                 bg=PAPER, fg=INK, anchor="w",
                 font=("Segoe UI", 11, "bold")).pack(fill="x", pady=(2, 3))
        self.order_vars = {}
        for name, color in ORDER_COLORS.items():
            row = tk.Frame(main, bg=color, highlightthickness=1, highlightbackground=INK)
            row.pack(fill="x", pady=2)
            tk.Button(row, text=name, command=lambda n=name: self.select_order(n),
                      bg=color, fg=INK, activebackground=PALE, relief="solid",
                      bd=1, width=12, font=("Segoe UI", 9, "bold")).pack(side="left", padx=3, pady=3)
            var = tk.StringVar(value="—")
            self.order_vars[name] = var
            out = tk.Entry(row, textvariable=var, state="readonly",
                           readonlybackground=color, fg=INK, relief="flat",
                           font=("Consolas", 10))
            out.pack(side="left", fill="x", expand=True, padx=8, ipady=7)

        self.tip = tk.StringVar(value=self.WALK_TIPS[self.order.get()])
        tk.Label(main, textvariable=self.tip, bg=PAPER, fg=MUTED,
                 anchor="w", font=("Segoe UI", 9)).pack(fill="x", pady=(4, 1))

        footer = tk.Frame(self, bg=PAPER)
        footer.pack(fill="x", padx=22, pady=(5, 10))
        self.facts = tk.StringVar()
        tk.Label(footer, textvariable=self.facts, bg=PAPER, fg=INK,
                 anchor="w", font=("Segoe UI", 9, "bold")).pack(fill="x")
        self.status = tk.StringVar(value="Select a node or build a tree to begin.")
        tk.Label(footer, textvariable=self.status, bg=PAPER, fg=MUTED,
                 anchor="w", font=("Segoe UI", 9)).pack(fill="x", pady=(3, 0))
        self._show_build_mode()
        self._refresh_facts()

    def _heading(self, parent, text):
        tk.Label(parent, text=text, bg=PAPER, fg=INK,
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(10, 5))

    def _label(self, parent, text):
        tk.Label(parent, text=text, bg=PAPER, fg=MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(5, 3))

    def _button(self, parent, text, command, color):
        return tk.Button(parent, text=text, command=command, bg=color, fg=INK,
                         activebackground=PALE, relief="solid", bd=1,
                         cursor="hand2", font=("Segoe UI", 9, "bold"),
                         padx=6, pady=5)

    def _show_build_mode(self):
        self.manual_box.pack_forget()
        self.values_box.pack_forget()
        if self.mode.get() == "Build manually":
            self.manual_box.pack(fill="x")
        else:
            self.values_box.pack(fill="x")
        if hasattr(self, "root_button"):
            self.root_button.configure(state="normal" if self.root_node is None else "disabled")

    def _valid_label(self):
        label = self.value_text.get().strip()
        if not label:
            messagebox.showinfo("Enter a value", "Type a short name or value for the new node.")
            return None
        if len(label) > 12:
            messagebox.showinfo("Keep it short", "Use 12 characters or fewer so node labels fit.")
            return None
        return label

    def add_root(self):
        if self.root_node is not None:
            messagebox.showinfo("Root already exists", "Clear the tree first to create a different root.")
            return
        label = self._valid_label()
        if label is None:
            return
        self.root_node = self.selected = Node(label)
        self.value_text.set("")
        self._changed(f"Created {label} as the root (trailhead).")

    def add_child(self, side):
        if self.root_node is None:
            messagebox.showinfo("Create the root first", "Add the root node before adding children.")
            return
        if self.selected is None:
            messagebox.showinfo("Select a parent", "Click a node on the map to select its parent.")
            return
        if getattr(self.selected, side) is not None:
            messagebox.showinfo("Child slot is occupied", f"{self.selected.label} already has a {side} child.")
            return
        if len(preorder(self.root_node)) >= 63:
            messagebox.showinfo("Tree is full", "This learning view supports up to 63 nodes.")
            return
        label = self._valid_label()
        if label is None:
            return
        child = Node(label, parent=self.selected)
        setattr(self.selected, side, child)
        parent_label = self.selected.label
        self.selected = child
        self.value_text.set("")
        self._changed(f"{label} is now the {side} child of {parent_label}.")

    def build_from_values(self):
        try:
            root = build_values(self.value_text.get(), self.arrangement.get())
        except ValueError as exc:
            messagebox.showerror("Couldn't build the tree", str(exc))
            return
        self.root_node = root
        self.selected = root
        self.mode.set("Build from values")
        self._show_build_mode()
        self._changed(f"Built a {self.arrangement.get().lower()} from your values.")
        if self.arrangement.get() == "Binary search tree":
            self.status.set("BST rule: smaller values go left; equal or larger values go right.")

    def remove_selected(self):
        node = self.selected
        if node is None:
            return
        if node.parent is None:
            self.clear_tree()
            return
        parent = node.parent
        side = "left" if parent.left is node else "right"
        setattr(parent, side, None)
        self.selected = parent
        self._changed(f"Removed {node.label} and its whole subtree.")

    def clear_tree(self):
        self.pause()
        self.root_node = self.selected = self.highlight = None
        self.sequence = []
        self.step_index = 0
        self.value_text.set("")
        self.node_info.set("Click a node to learn about its place in the tree.")
        self.status.set("Tree cleared. Create a root or build from a list of values.")
        self._refresh_facts()
        self._refresh_traversals()
        self._show_build_mode()
        self.draw()

    def _load_example(self):
        self.pause()
        nodes = {v: Node(v) for v in ("8", "4", "12", "2", "6", "10", "14")}
        for parent, side, child in (
            ("8", "left", "4"), ("8", "right", "12"),
            ("4", "left", "2"), ("4", "right", "6"),
            ("12", "left", "10"), ("12", "right", "14"),
        ):
            setattr(nodes[parent], side, nodes[child])
            nodes[child].parent = nodes[parent]
        self.root_node = self.selected = nodes["8"]
        self.highlight = None
        self.mode.set("Build from values")
        self.value_text.set("8 4 12 2 6 10 14")
        self.arrangement.set("Binary search tree")
        self._show_build_mode()
        self._changed("Example loaded. Click a node to inspect it or edit the tree.")
        self.tip.set(self.WALK_TIPS[self.order.get()])
        self.draw()

    def _changed(self, message):
        self.pause()
        self.highlight = None
        self.sequence = self.TRAVERSALS[self.order.get()](self.root_node)
        self.step_index = 0
        self.status.set(message)
        self._refresh_facts()
        self._refresh_traversals()
        self._show_build_mode()
        self.draw()

    def _refresh_traversals(self):
        for name, fn in self.TRAVERSALS.items():
            self.order_vars[name].set("  →  ".join(n.label for n in fn(self.root_node)) or "—")

    def _refresh_facts(self):
        if self.root_node is None:
            self.facts.set("Nodes: 0   •   Height: —   •   Balanced: —   •   Full: —   •   Complete: —")
            return
        count = len(preorder(self.root_node))
        h = height(self.root_node)
        self.facts.set(
            f"Nodes: {count}   •   Height: {h} edge(s)   •   "
            f"Balanced: {'yes' if is_balanced(self.root_node) else 'no'}   •   "
            f"Full: {'yes' if is_full(self.root_node) else 'no'}   •   "
            f"Complete: {'yes' if is_complete(self.root_node) else 'no'}"
        )

    def select_order(self, name=None):
        self.pause()
        if name is not None:
            self.order.set(name)
        self.tip.set(self.WALK_TIPS[self.order.get()])
        self.sequence = self.TRAVERSALS[self.order.get()](self.root_node)
        self.step_index = 0
        self.highlight = None
        self.status.set(f"{self.order.get()}: {self.tip.get()}")
        self.draw()

    def reset_walk(self):
        self.pause()
        self.sequence = self.TRAVERSALS[self.order.get()](self.root_node)
        self.step_index = 0
        self.highlight = None
        self.tip.set(self.WALK_TIPS[self.order.get()])
        self.status.set(f"{self.order.get()} reset. {self.tip.get()}")
        self.draw()

    def step(self):
        self.pause()
        self._advance(False)

    def play(self):
        if self.timer:
            self.pause()
            self.play_button.configure(text="Play")
            self.status.set("Traversal paused.")
            return
        if not self.sequence:
            self.status.set("Build a tree before starting a traversal.")
            return
        if self.step_index >= len(self.sequence):
            self.step_index = 0
        self.play_button.configure(text="Pause")
        self._advance(True)

    def _advance(self, autoplay):
        if not self.sequence:
            self.status.set("Build a tree before starting a traversal.")
            return
        if self.step_index >= len(self.sequence):
            self.step_index = 0
        node = self.sequence[self.step_index]
        self.highlight = node
        self.selected = node
        self.step_index += 1
        visited = "  →  ".join(n.label for n in self.sequence[:self.step_index])
        self.status.set(
            f"{self.order.get()} • visit {node.label} ({self.step_index}/{len(self.sequence)}): {visited}"
        )
        self._describe(node)
        self.draw()
        if autoplay:
            if self.step_index < len(self.sequence):
                self.timer = self.after(650, self._play_next)
            else:
                self.timer = None
                self.play_button.configure(text="Play")

    def _play_next(self):
        self.timer = None
        self._advance(True)

    def pause(self):
        if self.timer:
            self.after_cancel(self.timer)
            self.timer = None
        if hasattr(self, "play_button"):
            self.play_button.configure(text="Play")

    def select_at(self, event):
        for node, (x, y) in self.positions.items():
            if (event.x - x) ** 2 + (event.y - y) ** 2 <= 31 ** 2:
                self.pause()
                self.selected = node
                self.highlight = None
                self._describe(node)
                self.draw()
                self._show_build_mode()
                return

    def _describe(self, node):
        parent = node.parent.label if node.parent else "none (root)"
        children = [n.label for n in (node.left, node.right) if n]
        kind = "leaf" if not children else ("internal node" if node.parent else "root with children")
        ancestors = []
        current = node.parent
        while current:
            ancestors.append(current.label)
            current = current.parent
        route = " → ".join(reversed(ancestors) + [node.label]) if ancestors else node.label
        self.node_info.set(
            f"{node.label}: {kind}  •  parent: {parent}  •  children: {', '.join(children) or 'none'}"
            f"  •  level: {depth(node)}  •  route: {route}"
        )
        self.selected_label.set(f"Selected parent: {node.label} (level {depth(node)})")

    def _positions(self):
        nodes = inorder(self.root_node)
        if not nodes:
            return {}
        width = max(self.canvas.winfo_width(), 500)
        height_px = max(self.canvas.winfo_height(), 220)
        max_depth = max(depth(n) for n in nodes)
        gap = min(135, (width - 110) / max(1, len(nodes) - 1))
        start_x = (width - gap * (len(nodes) - 1)) / 2
        vertical = min(100, (height_px - 100) / max(1, max_depth))
        return {node: (start_x + i * gap, 54 + depth(node) * vertical)
                for i, node in enumerate(nodes)}

    def draw(self):
        if not hasattr(self, "canvas"):
            return
        c = self.canvas
        c.delete("all")
        width, height_px = c.winfo_width(), c.winfo_height()
        for x in range(18, width, 38):
            for y in range(18, height_px, 38):
                c.create_oval(x, y, x + 1, y + 1, fill="#354047", outline="")
        self.positions = self._positions()
        if not self.positions:
            c.create_text(width / 2, height_px / 2 - 12, text="Start by creating a root",
                          fill=PALE, font=("Segoe UI", 19, "bold"))
            c.create_text(width / 2, height_px / 2 + 20,
                          text="Use the controls on the left to build your own tree.",
                          fill="#b6c2c5", font=("Segoe UI", 10))
            return

        route = set()
        node = self.highlight
        while node:
            route.add(node)
            node = node.parent
        for parent, (x, y) in self.positions.items():
            for side, child in (("left", parent.left), ("right", parent.right)):
                direction = -1 if side == "left" else 1
                if child is not None:
                    xx, yy = self.positions[child]
                    color = GOLD if parent in route and child in route else "#aebfc1"
                    c.create_line(x, y + 24, xx, yy - 24, fill=color, width=3)
                    c.create_text((x + xx) / 2, (y + yy) / 2 - 4,
                                  text=side.upper(), fill="#d4dfe0",
                                  font=("Segoe UI", 8, "bold"))
                else:
                    cx, cy = x + direction * 34, y + 47
                    c.create_line(x, y + 22, cx, cy, fill="#53656a",
                                  width=1, dash=(3, 4))
                    c.create_oval(cx - 2, cy - 2, cx + 2, cy + 2,
                                  fill="#62767b", outline="")
        for node, (x, y) in self.positions.items():
            fill = GOLD if node is self.highlight else TEAL if node is self.selected else BLUE if node is self.root_node else "#344951"
            radius_x = 34 if len(node.label) > 7 else 29
            c.create_oval(x-radius_x, y-24, x+radius_x, y+24,
                          fill=fill, outline=PALE, width=2)
            c.create_text(x, y, text=node.label, fill=INK if node in (self.highlight, self.selected, self.root_node) else PALE,
                          font=("Segoe UI", 9, "bold"), width=radius_x * 2 - 4)
            tag = "ROOT" if node is self.root_node else "LEAF" if node.left is None and node.right is None else ""
            if tag:
                c.create_text(x, y-36, text=tag, fill="#d4dfe0",
                              font=("Segoe UI", 8, "bold"))
        c.create_text(12, 13,
                      text=f"{len(self.positions)} NODES  •  HEIGHT {height(self.root_node)} EDGES",
                      anchor="w", fill="#b6c2c5", font=("Segoe UI", 9, "bold"))


if __name__ == "__main__":
    TrailTreeExplorer().mainloop()
