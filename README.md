# Structure Lab | Binary Tree Workbench

A Python desktop program for learning what binary trees look like and how they work. The interface uses an engineering workbench style while keeping manual tree creation and traversal controls easy to find.

## Run

Use Python 3.10 or newer with Tkinter enabled:

```powershell
python main.py
```

No third-party packages are required.

## Build your own tree

### Manual mode

1. Choose **Build manually**.
2. Type a short node label and click **Set as root**.
3. Click a node on the canvas to select its parent.
4. Type another label and choose **+ Left child** or **+ Right child**.
5. Repeat to grow the tree. Select a node and choose **Remove selected subtree** to remove it and all descendants.

Manual labels and bulk numeric values have separate fields, so switching build modes will not mix their input.

### Build an expression tree

Choose **Build expression tree** and enter an arithmetic expression, for example `(3 + 4) * 2` or `a * (b + 5)`. Select **Build expression tree** to visualize it. Operators become parent nodes and numbers or variable names become operand leaves. Parentheses and operator precedence are respected. Supported operators are `+`, `-`, `*`, `/`, `//`, `%`, and `**`, including unary signs. Input is parsed as an expression; it is not executed as Python code. The same traversal controls work with expression trees.

### Build from values

Choose **Build from values**, enter numeric values separated by spaces or commas, and select an arrangement:

- **Binary search tree:** inserts values in order. Smaller values go left; equal or larger values go right.
- **Level-filled tree:** fills the top level first, then each lower level from left to right.

The workspace supports up to 31 nodes to keep the canvas readable.

## Explore

- Click nodes to see their parent, children, type, level, and route from the root.
- Drag the canvas to pan, use the mouse wheel or zoom buttons to zoom, and choose **Fit** to recenter the tree.
- The depth grid, left/right branch labels, and node identifiers make the structure easier to inspect.
- The four traversal rows show preorder, inorder, postorder, and level-order results.
- Select a traversal, then use **Step** or **Play** to highlight its visiting order.
- The metric cards report node count, height, balance, fullness, and completeness.

## Tree terms

- **Root:** the only node without a parent.
- **Leaf:** a node with no children.
- **Internal node:** a non-root node with at least one child.
- **Level:** number of edges from the root to a node.
- **Height:** number of edges on the longest root-to-leaf path.
- **Balanced:** all leaves are at the same depth or within one level, following the lecture slides.
- **Full:** follows the lecture slides' definition: every internal node has two children and all leaves are at the same depth.
- **Complete:** every level is full except possibly the last, whose nodes are packed from left to right.
