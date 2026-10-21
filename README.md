# Trail Tree Explorer

A Python desktop program that teaches binary trees through a branching trail map: places are nodes, trails are edges, and the trailhead is the root.

## Run

Use Python 3.10 or newer with Tkinter enabled:

```powershell
python main.py
```

No third-party packages are required.

## Build your own tree

### Manual mode

1. Leave **Build manually** selected.
2. Type a short label and click **Set as root**.
3. Click a node on the map to select it as the parent.
4. Type another label and choose **Add left child** or **Add right child**.
5. Repeat to grow the tree. Select a node and choose **Remove selected subtree** to remove that node and all of its descendants.

### Build from values

Choose **Build from values**, enter numeric values separated by spaces or commas, and select an arrangement:

- **Binary search tree:** inserts values in the order entered. Smaller values go left; equal or larger values go right.
- **Level-filled tree:** fills the top level first, then each lower level from left to right.

## Explore

- Click nodes to see their parent, children, type, level, and route from the root.
- The four traversal rows show preorder, inorder, postorder, and level-order results.
- Select a traversal, then use **Step** or **Play** to highlight its visiting order.
- The summary reports node count, height, balance, fullness, and completeness.

The visualizer supports up to 63 nodes to keep the map readable. The general manual mode does not sort nodes.

## Tree terms

- **Root:** the only node without a parent.
- **Leaf:** a node with no children.
- **Internal node:** a non-root node with at least one child.
- **Level:** number of edges from the root to a node.
- **Height:** number of edges on the longest root-to-leaf path.
- **Balanced:** all leaves are at the same depth or within one level, following the lecture slides.
- **Full:** follows the lecture slides' definition: every internal node has two children and all leaves are at the same depth.
- **Complete:** every level is full except possibly the last, whose nodes are packed from left to right.
