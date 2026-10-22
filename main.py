"""Trail Tree Explorer: a user-friendly binary-tree workbench.

Run with Python 3.10+:
    python main.py
No third-party packages are required.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import math
import ast
import operator
import tkinter as tk
from tkinter import messagebox, ttk


BG = "#101820"
PANEL = "#192630"
PANEL_RAISED = "#21323d"
CANVAS_BG = "#0d151b"
GRID = "#1b2a34"
GRID_MAJOR = "#263b47"
TEXT = "#e8f0f3"
MUTED = "#91a5af"
CYAN = "#37d6c7"
BLUE = "#56a9ff"
GREEN = "#65d99a"
AMBER = "#ffbd59"
RED = "#ff7d73"
EDGE = "#718894"
ORDER_COLORS = {
    "Preorder": "#e9b949",
    "Inorder": "#38c9a2",
    "Postorder": "#fa806c",
    "Level-order": "#4da5ef",
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
    output = []
    queue = deque([root] if root else [])
    while queue:
        node = queue.popleft()
        output.append(node)
        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)
    return output


def depth(node):
    value = 0
    while node.parent:
        value += 1
        node = node.parent
    return value


def height(node):
    if node is None:
        return -1
    return 1 + max(height(node.left), height(node.right))


def leaf_nodes(root):
    return [node for node in preorder(root) if node.left is None and node.right is None]


def is_balanced(root):
    depths = [depth(node) for node in leaf_nodes(root)]
    return bool(depths) and max(depths) - min(depths) <= 1


def is_full(root):
    if root is None:
        return False
    leaves_share_level = len({depth(node) for node in leaf_nodes(root)}) == 1
    each_internal_has_two = all(
        (node.left is None) == (node.right is None) for node in preorder(root)
    )
    return leaves_share_level and each_internal_has_two


def is_complete(root):
    if root is None:
        return False
    queue = deque([root])
    found_empty_slot = False
    while queue:
        node = queue.popleft()
        for child in (node.left, node.right):
            if child is None:
                found_empty_slot = True
            elif found_empty_slot:
                return False
            else:
                queue.append(child)
    return True



_ALLOWED_BINARY_OPERATORS = {
    ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/",
    ast.FloorDiv: "//", ast.Mod: "%", ast.Pow: "**",
}


def build_expression(raw):
    """Parse arithmetic into a tree without evaluating or executing the input."""
    if not raw.strip():
        raise ValueError("Enter an arithmetic expression, such as (3 + 4) * 2.")
    try:
        parsed = ast.parse(raw, mode="eval")
    except SyntaxError:
        raise ValueError("That expression is not valid. Check your operators and parentheses.") from None

    count = 0
    def convert(item):
        nonlocal count
        count += 1
        if count > 31:
            raise ValueError("Use an expression with 31 nodes or fewer so it remains readable.")
        if isinstance(item, ast.BinOp) and type(item.op) in _ALLOWED_BINARY_OPERATORS:
            node = Node(_ALLOWED_BINARY_OPERATORS[type(item.op)])
            node.left = convert(item.left)
            node.left.parent = node
            node.right = convert(item.right)
            node.right.parent = node
            return node
        if isinstance(item, ast.UnaryOp) and isinstance(item.op, (ast.UAdd, ast.USub)):
            node = Node("u+" if isinstance(item.op, ast.UAdd) else "u-")
            node.left = convert(item.operand)
            node.left.parent = node
            return node
        if isinstance(item, ast.Constant) and isinstance(item.value, (int, float)) and not isinstance(item.value, bool):
            return Node(str(item.value))
        if isinstance(item, ast.Name):
            return Node(item.id)
        raise ValueError("Use numbers, variable names, parentheses, and +, -, *, /, //, %, or ** only.")

    root = convert(parsed.body)
    return root


def parse_values(raw):
    tokens = raw.replace(",", " ").split()
    if not tokens:
        raise ValueError("Enter at least one number.")
    if len(tokens) > 31:
        raise ValueError("Use 31 values or fewer so the tree remains easy to read.")
    parsed = []
    for token in tokens:
        try:
            number = float(token)
        except ValueError:
            raise ValueError(f"{token!r} is not a number. Use spaces or commas between values.") from None
        if not math.isfinite(number):
            raise ValueError("Values must be finite numbers.")
        parsed.append((token, number))
    return parsed


def build_values(raw, arrangement):
    values = parse_values(raw)
    nodes = [Node(label) for label, _number in values]
    if arrangement == "Level-filled tree":
        for index, node in enumerate(nodes):
            if 2 * index + 1 < len(nodes):
                node.left = nodes[2 * index + 1]
                node.left.parent = node
            if 2 * index + 2 < len(nodes):
                node.right = nodes[2 * index + 2]
                node.right.parent = node
        return nodes[0]

    numeric = {node: values[index][1] for index, node in enumerate(nodes)}
    root = nodes[0]
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
        "Preorder": "Visit the parent, then its left subtree, then its right subtree.",
        "Inorder": "Visit the left subtree, then the parent, then the right subtree.",
        "Postorder": "Visit both subtrees before their parent.",
        "Level-order": "Visit one level at a time, scanning from left to right.",
    }

    def __init__(self):
        super().__init__()
        self.title("Structure Lab | Binary Tree Workbench")
        self.geometry("1440x900")
        self.minsize(1120, 760)
        self.configure(bg=BG)

        self.root_node = None
        self.selected = None
        self.highlight = None
        self.base_positions = {}
        self.positions = {}
        self.scale = 1.0
        self.offset = [0.0, 0.0]
        self.last_drag = None
        self.order = tk.StringVar(value="Preorder")
        self.mode = tk.StringVar(value="Build manually")
        self.arrangement = tk.StringVar(value="Binary search tree")
        self.node_label = tk.StringVar()
        self.value_text = tk.StringVar()
        self.sequence = []
        self.step_index = 0
        self.timer = None

        self._build_ui()
        self._load_example()

    def _build_ui(self):
        self._configure_style()
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=18, pady=(12, 8))
        title_group = tk.Frame(header, bg=BG)
        title_group.pack(side="left")
        tk.Label(title_group, text="STRUCTURE LAB", bg=BG, fg=TEXT,
                 font=("Segoe UI", 20, "bold")).pack(side="left")
        tk.Label(title_group, text="  /  BINARY TREE WORKBENCH", bg=BG,
                 fg=CYAN, font=("Consolas", 10, "bold")).pack(side="left", padx=(8, 0), pady=(6, 0))
        self.header_state = tk.StringVar(value="READY")
        tk.Label(header, textvariable=self.header_state, bg=PANEL,
                 fg=GREEN, font=("Consolas", 9, "bold"), padx=12, pady=7).pack(side="right")

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=18, pady=(0, 7))
        sidebar = tk.Frame(body, bg=BG, width=285)
        sidebar.pack(side="left", fill="y", padx=(0, 14))
        sidebar.pack_propagate(False)
        work = tk.Frame(body, bg=BG)
        work.pack(side="left", fill="both", expand=True)

        self._panel_heading(sidebar, "01  BUILD STRUCTURE")
        tk.Label(sidebar, text="Choose a build method", bg=BG, fg=MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(2, 4))
        mode = ttk.Combobox(sidebar, textvariable=self.mode,
                            values=("Build manually", "Build from values", "Build expression tree"),
                            state="readonly")
        mode.pack(fill="x")
        mode.bind("<<ComboboxSelected>>", lambda _e: self._show_mode())

        self.build_area = tk.Frame(sidebar, bg=BG)
        self.build_area.pack(fill="x")
        self.manual_box = tk.Frame(self.build_area, bg=BG)
        self._small_label(self.manual_box, "NODE LABEL")
        self.value_entry = tk.Entry(
            self.manual_box, textvariable=self.node_label, bg=PANEL,
            fg=TEXT, insertbackground=CYAN, relief="flat",
            highlightthickness=1, highlightbackground="#3a505e",
            highlightcolor=CYAN, font=("Segoe UI", 11)
        )
        self.value_entry.pack(fill="x", ipady=8)
        self.value_entry.bind("<Return>", lambda _e: self._enter_key_action())
        self.selection_var = tk.StringVar(value="Parent: none selected")
        tk.Label(self.manual_box, textvariable=self.selection_var, bg=BG,
                 fg=MUTED, font=("Segoe UI", 9), anchor="w",
                 wraplength=275, justify="left").pack(fill="x", pady=(7, 4))
        self.root_button = self._button(self.manual_box, "Set as root", self.add_root, BLUE)
        self.root_button.pack(fill="x", pady=3)
        child_buttons = tk.Frame(self.manual_box, bg=BG)
        child_buttons.pack(fill="x", pady=3)
        self._button(child_buttons, "+ Left child", lambda: self.add_child("left"), CYAN).pack(side="left", expand=True, fill="x", padx=(0, 3))
        self._button(child_buttons, "+ Right child", lambda: self.add_child("right"), CYAN).pack(side="left", expand=True, fill="x", padx=(3, 0))
        self._button(self.manual_box, "Remove selected subtree", self.remove_selected, RED).pack(fill="x", pady=3)
        tk.Label(self.manual_box,
                 text="Click a node in the map to choose its parent. A binary node has at most one left and one right child.",
                 bg=BG, fg=MUTED, font=("Segoe UI", 8), wraplength=272,
                 justify="left").pack(anchor="w", pady=(5, 0))

        self.values_box = tk.Frame(self.build_area, bg=BG)
        self._small_label(self.values_box, "VALUES  •  NUMBERS SEPARATED BY SPACES OR COMMAS")
        self.value_entry_values = tk.Entry(
            self.values_box, textvariable=self.value_text, bg=PANEL,
            fg=TEXT, insertbackground=CYAN, relief="flat",
            highlightthickness=1, highlightbackground="#3a505e",
            highlightcolor=CYAN, font=("Segoe UI", 10)
        )
        self.value_entry_values.pack(fill="x", ipady=8)
        self._small_label(self.values_box, "ARRANGEMENT")
        arrangement = ttk.Combobox(self.values_box, textvariable=self.arrangement,
                                   values=("Binary search tree", "Level-filled tree"),
                                   state="readonly")
        arrangement.pack(fill="x")
        tk.Label(self.values_box,
                 text="BST inserts in order: smaller values go left. Level-filled places values row by row.",
                 bg=BG, fg=MUTED, font=("Segoe UI", 8), wraplength=272,
                 justify="left").pack(anchor="w", pady=(6, 3))
        self._button(self.values_box, "Build from values", self.build_from_values, BLUE).pack(fill="x", pady=3)
        self.value_entry_values.bind("<Return>", lambda _e: self.build_from_values())

        self.expression_box = tk.Frame(self.build_area, bg=BG)
        self._small_label(self.expression_box, "ARITHMETIC EXPRESSION")
        self.expression_text = tk.StringVar(value="(3 + 4) * 2")
        self.expression_entry = tk.Entry(
            self.expression_box, textvariable=self.expression_text, bg=PANEL,
            fg=TEXT, insertbackground=CYAN, relief="flat",
            highlightthickness=1, highlightbackground="#3a505e",
            highlightcolor=CYAN, font=("Consolas", 11)
        )
        self.expression_entry.pack(fill="x", ipady=8)
        tk.Label(self.expression_box,
                 text="Builds an expression tree using operator nodes and operand leaves. Supports +, -, *, /, //, %, **, unary signs, and parentheses.",
                 bg=BG, fg=MUTED, font=("Segoe UI", 8), wraplength=272,
                 justify="left").pack(anchor="w", pady=(6, 3))
        self._button(self.expression_box, "Build expression tree", self.build_expression_tree, BLUE).pack(fill="x", pady=3)
        self.expression_entry.bind("<Return>", lambda _e: self.build_expression_tree())

        quick = tk.Frame(sidebar, bg=BG)
        quick.pack(fill="x", pady=(7, 4))
        self._button(quick, "Load example", self._load_example, AMBER).pack(side="left", expand=True, fill="x", padx=(0, 3))
        self._button(quick, "New tree", self.clear_tree, PANEL_RAISED).pack(side="left", expand=True, fill="x", padx=(3, 0))

        self._panel_heading(sidebar, "02  TRAVERSAL CONTROL")
        tk.Label(sidebar, text="VISIT ORDER", bg=BG, fg=MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(1, 4))
        order_box = ttk.Combobox(sidebar, textvariable=self.order,
                                 values=list(self.TRAVERSALS), state="readonly")
        order_box.pack(fill="x")
        order_box.bind("<<ComboboxSelected>>", lambda _e: self.select_order())
        controls = tk.Frame(sidebar, bg=BG)
        controls.pack(fill="x", pady=6)
        self._button(controls, "Step", self.step, BLUE).pack(side="left", expand=True, fill="x", padx=(0, 3))
        self.play_button = self._button(controls, "Play", self.play, CYAN)
        self.play_button.pack(side="left", expand=True, fill="x", padx=3)
        self._button(controls, "Reset", self.reset_walk, PANEL_RAISED).pack(side="left", expand=True, fill="x", padx=(3, 0))
        self._small_label(sidebar, "MAP NAVIGATION")
        nav = tk.Frame(sidebar, bg=BG)
        nav.pack(fill="x", pady=(0, 5))
        self._button(nav, "−", lambda: self.zoom(0.82), PANEL_RAISED).pack(side="left", expand=True, fill="x", padx=(0, 3))
        self._button(nav, "Fit", self.fit_view, PANEL_RAISED).pack(side="left", expand=True, fill="x", padx=3)
        self._button(nav, "+", lambda: self.zoom(1.22), PANEL_RAISED).pack(side="left", expand=True, fill="x", padx=(3, 0))

        topbar = tk.Frame(work, bg=BG)
        topbar.pack(fill="x", pady=(0, 6))
        tk.Label(topbar, text="TREE CANVAS", bg=BG, fg=TEXT,
                 font=("Segoe UI", 12, "bold")).pack(side="left")
        tk.Label(topbar, text="Select nodes to inspect  •  drag to pan  •  wheel to zoom",
                 bg=BG, fg=MUTED, font=("Segoe UI", 8)).pack(side="left", padx=12)
        self.canvas = tk.Canvas(work, bg=CANVAS_BG, highlightthickness=1,
                                highlightbackground="#354954", height=340)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda _e: self.draw())
        self.canvas.bind("<ButtonPress-1>", self.drag_start)
        self.canvas.bind("<B1-Motion>", self.drag_move)
        self.canvas.bind("<ButtonRelease-1>", self.drag_end)
        self.canvas.bind("<MouseWheel>", self.wheel_zoom)
        self.canvas.bind("<Button-4>", lambda e: self.zoom(1.12, e.x, e.y))
        self.canvas.bind("<Button-5>", lambda e: self.zoom(1 / 1.12, e.x, e.y))

        self._build_metrics(work)
        self.node_info = tk.StringVar(value="Click a node to inspect its connections and route from the root.")
        info_panel = tk.Frame(work, bg=PANEL, padx=10, pady=7)
        info_panel.pack(fill="x", pady=(6, 6))
        tk.Label(info_panel, text="SELECTED NODE", bg=PANEL, fg=CYAN,
                 font=("Consolas", 8, "bold")).pack(side="left", padx=(0, 9))
        tk.Label(info_panel, textvariable=self.node_info, bg=PANEL, fg=TEXT,
                 font=("Segoe UI", 9), anchor="w", justify="left",
                 wraplength=1000).pack(side="left", fill="x", expand=True)

        traversal_header = tk.Frame(work, bg=BG)
        traversal_header.pack(fill="x", pady=(2, 3))
        tk.Label(traversal_header, text="TRAVERSAL SEQUENCES", bg=BG,
                 fg=TEXT, font=("Segoe UI", 10, "bold")).pack(side="left")
        self.walk_tip = tk.StringVar(value=self.WALK_TIPS[self.order.get()])
        tk.Label(traversal_header, textvariable=self.walk_tip, bg=BG,
                 fg=MUTED, font=("Segoe UI", 8)).pack(side="right")
        self.order_vars = {}
        for name, color in ORDER_COLORS.items():
            row = tk.Frame(work, bg=color, highlightthickness=1, highlightbackground="#0b1116")
            row.pack(fill="x", pady=1)
            tk.Button(row, text=name.upper(), command=lambda n=name: self.select_order(n),
                      bg=color, fg="#10202a", activebackground="#f3f6f7",
                      relief="flat", bd=0, width=12,
                      font=("Consolas", 8, "bold")).pack(side="left", padx=(5, 2), pady=3)
            var = tk.StringVar(value="—")
            self.order_vars[name] = var
            result = tk.Entry(row, textvariable=var, state="readonly",
                              readonlybackground=color, fg="#10202a",
                              relief="flat", font=("Consolas", 9))
            result.pack(side="left", fill="x", expand=True, padx=7, ipady=5)

        self.status = tk.StringVar(value="Ready.")
        footer = tk.Frame(self, bg=BG)
        footer.pack(fill="x", padx=18, pady=(0, 8))
        tk.Label(footer, textvariable=self.status, bg=BG, fg=MUTED,
                 anchor="w", font=("Segoe UI", 8)).pack(fill="x")

        self._show_mode()
        self._refresh_metrics()
        self._refresh_sequences()

    def _configure_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TCombobox", fieldbackground=PANEL, background=PANEL,
                        foreground=TEXT, arrowcolor=CYAN, bordercolor="#3a505e",
                        padding=6)
        style.map("TCombobox",
                  fieldbackground=[("readonly", PANEL)],
                  foreground=[("readonly", TEXT)],
                  selectbackground=[("readonly", PANEL)],
                  selectforeground=[("readonly", TEXT)])

    def _panel_heading(self, parent, text):
        tk.Label(parent, text=text, bg=BG, fg=CYAN,
                 font=("Consolas", 10, "bold")).pack(anchor="w", pady=(10, 6))

    def _small_label(self, parent, text):
        tk.Label(parent, text=text, bg=BG, fg=MUTED,
                 font=("Consolas", 8, "bold")).pack(anchor="w", pady=(6, 3))

    def _button(self, parent, text, command, color):
        return tk.Button(parent, text=text, command=command, bg=color, fg="#101820",
                         activebackground="#d8f5f2", activeforeground="#101820",
                         relief="flat", bd=0, cursor="hand2",
                         font=("Segoe UI", 9, "bold"), padx=7, pady=6)

    def _show_mode(self):
        self.manual_box.pack_forget()
        self.values_box.pack_forget()
        self.expression_box.pack_forget()
        if self.mode.get() == "Build manually":
            self.manual_box.pack(fill="x")
        elif self.mode.get() == "Build from values":
            self.values_box.pack(fill="x")
        else:
            self.expression_box.pack(fill="x")
        if hasattr(self, "root_button"):
            self.root_button.configure(state="normal" if self.root_node is None else "disabled")

    def _enter_key_action(self):
        if self.root_node is None:
            self.add_root()
        elif self.selected is not None:
            side = "left" if self.selected.left is None else "right" if self.selected.right is None else None
            if side:
                self.add_child(side)
            else:
                messagebox.showinfo("Choose a child side", "Both child positions are occupied. Select another node.")

    def _label_value(self):
        label = self.node_label.get().strip()
        if not label:
            messagebox.showinfo("Enter a node label", "Type a short label for the new node.")
            return None
        if len(label) > 12:
            messagebox.showinfo("Shorten the label", "Use 12 characters or fewer so the node fits on the map.")
            return None
        return label

    def add_root(self):
        if self.root_node is not None:
            messagebox.showinfo("Root already exists", "Choose New tree before creating a different root.")
            return
        label = self._label_value()
        if label is None:
            return
        self.root_node = self.selected = Node(label)
        self.node_label.set("")
        self._changed(f"{label} is the root: the starting point of the tree.")

    def add_child(self, side):
        if self.root_node is None:
            messagebox.showinfo("Create a root first", "Create the root before adding child nodes.")
            return
        if self.selected is None:
            messagebox.showinfo("Select a parent", "Click a node on the map, then choose its left or right child.")
            return
        if getattr(self.selected, side) is not None:
            messagebox.showinfo("Position already occupied", f"{self.selected.label} already has a {side} child.")
            return
        if len(preorder(self.root_node)) >= 31:
            messagebox.showinfo("Tree size limit", "The visual workspace supports up to 31 nodes.")
            return
        label = self._label_value()
        if label is None:
            return
        parent_label = self.selected.label
        child = Node(label, parent=self.selected)
        setattr(self.selected, side, child)
        self.selected = child
        self.node_label.set("")
        self._changed(f"Added {label} as the {side} child of {parent_label}.")

    def build_from_values(self):
        try:
            root = build_values(self.value_text.get(), self.arrangement.get())
        except ValueError as error:
            messagebox.showerror("Couldn't build the tree", str(error))
            return
        self.root_node = self.selected = root
        self.mode.set("Build from values")
        self._show_mode()
        rule = ("Smaller values are placed left; equal or larger values right."
                if self.arrangement.get() == "Binary search tree"
                else "Values fill each level from left to right.")
        self._changed(f"Tree built. {rule}")

    def build_expression_tree(self):
        try:
            root = build_expression(self.expression_text.get())
        except ValueError as error:
            messagebox.showerror("Couldn't build the expression tree", str(error))
            return
        self.root_node = self.selected = root
        self.mode.set("Build expression tree")
        self._show_mode()
        self._changed("Expression tree built. Operators are parent nodes; operands are leaves.")

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
        self._changed(f"Removed {node.label} and all nodes below it.")

    def clear_tree(self):
        self.pause()
        self.root_node = self.selected = self.highlight = None
        self.sequence = []
        self.step_index = 0
        self.value_text.set("")
        self.node_label.set("")
        self.node_info.set("Click a node to inspect its connections and route from the root.")
        self.status.set("Workspace cleared. Create a root or build a tree from values.")
        self.mode.set("Build manually")
        self._show_mode()
        self._refresh_metrics()
        self._refresh_sequences()
        self.fit_view()

    def _load_example(self):
        self.pause()
        nodes = {label: Node(label) for label in ("8", "4", "12", "2", "6", "10", "14")}
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
        self.arrangement.set("Binary search tree")
        self.value_text.set("8 4 12 2 6 10 14")
        self._show_mode()
        self.node_info.set("Example root 8 has children 4 and 12. Click any node to inspect its family and level.")
        self._changed("Example loaded. Try selecting a traversal or make a change to the tree.")

    def _changed(self, message):
        self.pause()
        self.highlight = None
        self.sequence = self.TRAVERSALS[self.order.get()](self.root_node)
        self.step_index = 0
        self.status.set(message)
        self._refresh_metrics()
        self._refresh_sequences()
        self._show_mode()
        self.fit_view()

    def _refresh_metrics(self):
        for child in getattr(self, "metrics_inner", ()).winfo_children() if hasattr(self, "metrics_inner") else ():
            child.destroy()
        root = self.root_node
        values = [
            ("NODES", str(len(preorder(root))) if root else "0"),
            ("HEIGHT", f"{height(root)} edges" if root else "—"),
            ("BALANCED", "YES" if root and is_balanced(root) else "—" if not root else "NO"),
            ("FULL", "YES" if root and is_full(root) else "—" if not root else "NO"),
            ("COMPLETE", "YES" if root and is_complete(root) else "—" if not root else "NO"),
        ]
        if not hasattr(self, "metrics_inner"):
            return
        for title, value in values:
            card = tk.Frame(self.metrics_inner, bg=PANEL, padx=10, pady=5,
                            highlightthickness=1, highlightbackground="#2a3d48")
            card.pack(side="left", expand=True, fill="x", padx=2)
            tk.Label(card, text=title, bg=PANEL, fg=MUTED,
                     font=("Consolas", 7, "bold")).pack(anchor="w")
            tint = GREEN if value == "YES" else AMBER if title == "HEIGHT" else TEXT
            tk.Label(card, text=value, bg=PANEL, fg=tint,
                     font=("Segoe UI", 10, "bold")).pack(anchor="w")

    def _build_metrics(self, parent):
        self.metrics_inner = tk.Frame(parent, bg=BG)
        self.metrics_inner.pack(fill="x", pady=(6, 0))

    def _refresh_sequences(self):
        if not hasattr(self, "order_vars"):
            return
        for name, traversal in self.TRAVERSALS.items():
            self.order_vars[name].set("   →   ".join(n.label for n in traversal(self.root_node)) or "—")

    def select_order(self, name=None):
        self.pause()
        if name:
            self.order.set(name)
        self.walk_tip.set(self.WALK_TIPS[self.order.get()])
        self.sequence = self.TRAVERSALS[self.order.get()](self.root_node)
        self.step_index = 0
        self.highlight = None
        self.status.set(f"{self.order.get()} selected. {self.WALK_TIPS[self.order.get()]}")
        self.draw()

    def reset_walk(self):
        self.pause()
        self.sequence = self.TRAVERSALS[self.order.get()](self.root_node)
        self.step_index = 0
        self.highlight = None
        self.walk_tip.set(self.WALK_TIPS[self.order.get()])
        self.status.set(f"{self.order.get()} reset. {self.WALK_TIPS[self.order.get()]}")
        self.draw()

    def step(self):
        self.pause()
        self._advance(False)

    def play(self):
        if self.timer:
            self.pause()
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
        self._describe(node)
        visited = "  →  ".join(n.label for n in self.sequence[:self.step_index])
        self.status.set(
            f"{self.order.get()}  •  visit {node.label}  •  {self.step_index}/{len(self.sequence)}: {visited}"
        )
        self.draw()
        if autoplay and self.step_index < len(self.sequence):
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

    def _describe(self, node):
        self.selection_var.set(f"Parent: {node.label}  •  level {depth(node)}")
        parent = node.parent.label if node.parent else "none (root)"
        children = [child.label for child in (node.left, node.right) if child]
        kind = "leaf" if not children else "internal node" if node.parent else "root with children"
        ancestors = []
        current = node.parent
        while current:
            ancestors.append(current.label)
            current = current.parent
        route = " → ".join(list(reversed(ancestors)) + [node.label])
        self.node_info.set(
            f"{node.label}  •  {kind}  •  parent: {parent}  •  children: {', '.join(children) or 'none'}"
            f"  •  level: {depth(node)}  •  route: {route}"
        )

    def _base_layout(self):
        nodes = inorder(self.root_node)
        if not nodes:
            return {}
        max_depth = max(depth(node) for node in nodes)
        return {
            node: ((index - (len(nodes) - 1) / 2) * 105, depth(node) * 102)
            for index, node in enumerate(nodes)
        }

    def fit_view(self):
        self.update_idletasks()
        self.base_positions = self._base_layout()
        if not self.base_positions:
            self.scale = 1.0
            self.offset = [self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2]
            self.draw()
            return
        width = max(100, (len(self.base_positions) - 1) * 105 + 100)
        max_y = max(y for _x, y in self.base_positions.values()) + 80
        w = max(100, self.canvas.winfo_width() - 80)
        h = max(100, self.canvas.winfo_height() - 100)
        self.scale = max(0.18, min(1.15, w / width, h / max(100, max_y)))
        self.offset = [self.canvas.winfo_width() / 2, 52]
        self.draw()

    def zoom(self, factor, x=None, y=None):
        x = self.canvas.winfo_width() / 2 if x is None else x
        y = self.canvas.winfo_height() / 2 if y is None else y
        new_scale = max(0.18, min(2.2, self.scale * factor))
        ratio = new_scale / self.scale
        self.offset = [x + (self.offset[0] - x) * ratio,
                       y + (self.offset[1] - y) * ratio]
        self.scale = new_scale
        self.draw()

    def wheel_zoom(self, event):
        self.zoom(1.1 if event.delta > 0 else 1 / 1.1, event.x, event.y)

    def drag_start(self, event):
        self.last_drag = (event.x, event.y)

    def drag_move(self, event):
        if self.last_drag is None:
            return
        # Clicking and dragging a node pans the engineering canvas; a simple click selects it.
        x0, y0 = self.last_drag
        if abs(event.x - x0) + abs(event.y - y0) > 5:
            self.offset[0] += event.x - x0
            self.offset[1] += event.y - y0
            self.last_drag = (event.x, event.y)
            self.draw()

    def drag_end(self, event):
        if self.last_drag is None:
            return
        x0, y0 = self.last_drag
        if abs(event.x - x0) + abs(event.y - y0) <= 5:
            self.select_at(event)
        self.last_drag = None

    def select_at(self, event):
        for node, (x, y) in self.positions.items():
            if abs(event.x - x) <= 43 * self.scale and abs(event.y - y) <= 30 * self.scale:
                self.pause()
                self.selected = node
                self.highlight = None
                self._describe(node)
                self.draw()
                self._show_mode()
                return

    def draw(self):
        if not hasattr(self, "canvas"):
            return
        canvas = self.canvas
        canvas.delete("all")
        width, height_px = canvas.winfo_width(), canvas.winfo_height()
        for x in range(10, width, 24):
            major = (x // 24) % 4 == 0
            canvas.create_line(x, 0, x, height_px,
                               fill=GRID_MAJOR if major else GRID, width=1)
        for y in range(10, height_px, 24):
            major = (y // 24) % 4 == 0
            canvas.create_line(0, y, width, y,
                               fill=GRID_MAJOR if major else GRID, width=1)
        self.base_positions = self._base_layout()
        if not self.base_positions:
            canvas.create_text(width / 2, height_px / 2 - 15,
                               text="NO TREE LOADED", fill=TEXT,
                               font=("Consolas", 13, "bold"))
            canvas.create_text(width / 2, height_px / 2 + 12,
                               text="Create a root or build one from a list of values.",
                               fill=MUTED, font=("Segoe UI", 9))
            self.positions = {}
            return

        self.positions = {
            node: (self.offset[0] + x * self.scale,
                   self.offset[1] + y * self.scale)
            for node, (x, y) in self.base_positions.items()
        }
        max_depth = max(depth(node) for node in self.positions)
        for level in range(max_depth + 1):
            y = self.offset[1] + level * 102 * self.scale
            if -25 <= y <= height_px + 25:
                canvas.create_line(44, y, width, y, fill="#20323b",
                                   dash=(2, 6), width=1)
                canvas.create_text(35, y, text=f"D{level}", fill="#70858e",
                                  font=("Consolas", 7), anchor="e")

        route = set()
        current = self.highlight
        while current:
            route.add(current)
            current = current.parent
        for parent, (x, y) in self.positions.items():
            for side, child in (("left", parent.left), ("right", parent.right)):
                dx = -1 if side == "left" else 1
                if child:
                    xx, yy = self.positions[child]
                    line_color = AMBER if parent in route and child in route else EDGE
                    canvas.create_line(x, y + 25 * self.scale,
                                       xx, yy - 25 * self.scale,
                                       fill=line_color, width=max(1, 2 * self.scale),
                                       arrow=tk.LAST, arrowshape=(8, 10, 4))
                    canvas.create_text((x + xx) / 2, (y + yy) / 2,
                                       text="L" if side == "left" else "R",
                                       fill=CYAN if line_color != AMBER else AMBER,
                                       font=("Consolas", max(7, int(8 * self.scale)), "bold"))
                else:
                    gx, gy = x + dx * 35 * self.scale, y + 50 * self.scale
                    canvas.create_line(x, y + 22 * self.scale, gx, gy,
                                       fill="#354b56", dash=(3, 4), width=1)
                    canvas.create_oval(gx - 2, gy - 2, gx + 2, gy + 2,
                                       fill="#536a75", outline="")

        ordered = inorder(self.root_node)
        for number, (node, (x, y)) in enumerate(zip(ordered, [self.positions[n] for n in ordered]), start=1):
            is_current = node is self.highlight
            is_selected = node is self.selected
            if is_current:
                fill, outline, tag = "#553d20", AMBER, "CURRENT"
            elif is_selected:
                fill, outline, tag = "#164b4e", CYAN, "SELECTED"
            elif node is self.root_node:
                fill, outline, tag = "#174535", GREEN, "ROOT"
            else:
                fill, outline, tag = PANEL_RAISED, "#6b828d", "LEAF" if not node.left and not node.right else "NODE"
            half_w, half_h = 43 * self.scale, 25 * self.scale
            canvas.create_rectangle(x - half_w, y - half_h, x + half_w, y + half_h,
                                    fill=fill, outline=outline, width=max(1, 2 * self.scale))
            canvas.create_text(x, y - 8 * self.scale, text=node.label,
                               fill=TEXT, font=("Segoe UI", max(7, int(10 * self.scale)), "bold"),
                               width=80 * self.scale)
            canvas.create_text(x, y + 12 * self.scale,
                               text=f"N{number:02d}  /  D{depth(node)}  /  {tag}",
                               fill=CYAN if is_selected else MUTED,
                               font=("Consolas", max(5, int(6 * self.scale))))
        canvas.create_text(12, 12,
                           text=f"{len(ordered):02d} NODES    HEIGHT {height(self.root_node)}    SCALE {self.scale:.0%}",
                           fill=MUTED, anchor="nw",
                           font=("Consolas", 8, "bold"))

    def _build_metrics(self, parent):
        self.metrics_inner = tk.Frame(parent, bg=BG)
        self.metrics_inner.pack(fill="x", pady=(6, 0))

    def _refresh_metrics(self):
        if not hasattr(self, "metrics_inner"):
            return
        for child in self.metrics_inner.winfo_children():
            child.destroy()
        root = self.root_node
        metrics = [
            ("NODE COUNT", str(len(preorder(root))) if root else "0"),
            ("HEIGHT", f"{height(root)} edges" if root else "—"),
            ("BALANCED", "YES" if root and is_balanced(root) else "—" if not root else "NO"),
            ("FULL", "YES" if root and is_full(root) else "—" if not root else "NO"),
            ("COMPLETE", "YES" if root and is_complete(root) else "—" if not root else "NO"),
        ]
        for name, value in metrics:
            card = tk.Frame(self.metrics_inner, bg=PANEL, padx=9, pady=4,
                            highlightthickness=1, highlightbackground="#2a3d48")
            card.pack(side="left", expand=True, fill="x", padx=2)
            tk.Label(card, text=name, bg=PANEL, fg=MUTED,
                     font=("Consolas", 7, "bold")).pack(anchor="w")
            color = GREEN if value == "YES" else AMBER if name == "HEIGHT" else TEXT
            tk.Label(card, text=value, bg=PANEL, fg=color,
                     font=("Segoe UI", 9, "bold")).pack(anchor="w")

    def _refresh_sequences(self):
        if not hasattr(self, "order_vars"):
            return
        for name, traversal in self.TRAVERSALS.items():
            self.order_vars[name].set("   →   ".join(node.label for node in traversal(self.root_node)) or "—")


if __name__ == "__main__":
    TrailTreeExplorer().mainloop()
