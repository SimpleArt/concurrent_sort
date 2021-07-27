Different sorting algorithms have different advantages and applications. This repo contains implementations of heap- and treap-sort, which are two sorting algorithms specialized towards concurrency and sorting as it goes. This is opposed to the built-in sorting algorithms, which requires all of the data to be collected before then sorting the entire thing all at once.

Heap-sort offers the advantage of producing results quickly. This is useful if one only wants the first few sorted values, or if receiving results quickly is beneficial because processing them can be slow.

Treap-sort offers the advantage of building the sorted structure as items are received. This is useful if the values are produced slowly, allowing sorting to happen simultaneously.

The disadvantage of each however is that their overhead may be larger than that of the built-in sort. This includes taking up more space or being cache inefficient. They also don't take advantage of partially sorted data.

The `Treap` data structure is also included. For example:

```python
>>> print(Treap(range(20)))
                   6
                  / \
                 /   \
                /     \
               /       \
              /         \
             /           \
            /             \
           /               \
          /                 \
         /                   \
        /                     \
       /                       10
      /                       / \
     /                       /   \
    /                       /     \
   /                       /       \
  /                       /         \
 0                       /           \
/ \                     /             \
   \                   /               \
    \                 7                 \
     \               / \                 \
      \                 \                 \
       2                 \                 \
      / \                 \                 \
     /   \                 \                 \
    1     \                 9                 15
   / \     \               / \               / \
            \             /                 /   \
             \           8                 /     \
              \         / \               /       \
               \                         /         \
                5                       /           \
               / \                     /             \
              /                       /               \
             4                       12                18
            / \                     / \               / \
           /                       /   \             /   \
          3                       11    13          17    19
         / \                     / \   / \         / \   / \
                                          \       /
                                           14    16
                                          / \   / \
```

And you can build a `Treap` from scratch yourself:

```python
treap = Treap()
for i in range(20):
    treap.insert(i)
    print(treap)
```
