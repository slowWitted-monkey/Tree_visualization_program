# Trail Tree Explorer

A small Python desktop program for learning how binary trees look and work. It uses a branching trail map as its teaching analogy: places are nodes, trails are edges, and the trailhead is the root.

## Run

Use Python 3.10 or newer with Tkinter enabled:

```powershell
python main.py
```

No third-party packages are required.

## Explore

- Click **Load example trail** to see a root, two children, and a deeper subtree.
- Click a place to inspect its parent, children, node type, level, and subtree size.
- Enter a name and add it as the root or as a left/right child of the selected place.
- Missing child slots are shown as ghost branches to make the two-child limit visible.
- Step or play a preorder, inorder, postorder, or level-order traversal. The current place and route are highlighted.
- Watch the summary update with node count, height, balance, fullness, and completeness.
- Remove a selected place to remove its entire subtree.

## Terms used

- **Node / place:** a stored element in the hierarchy.
- **Edge / trail:** a connection from a parent to a child.
- **Root / trailhead:** the only node without a parent.
- **Leaf / destination:** a node with no children.
- **Internal node:** a non-root node with at least one child.
- **Level:** number of edges from the root to a node.
- **Height:** number of edges along the longest root-to-leaf path.
- **Balanced:** all leaves are at the same depth or within one level, following the lecture slides.
- **Full:** uses the lecture slides' definition: every internal node has two children and all leaves are at the same depth.
- **Complete:** every level is full except possibly the last, whose nodes are packed left to right.

The tree is a general binary tree. Adding a child does not sort values or enforce binary-search-tree ordering.

## Project files

- `main.py`: the interface, tree model, drawing, facts, and traversal animation.
