"""
Implementation of treap sort to sort results as they are received.

>>> print(*treap_sort([1, 7, 8, 0, 4, 6, 2, 3, 5]))
0 1 2 3 4 5 6 7 8
"""
from __future__ import annotations
from typing import runtime_checkable, Generic, Iterable, Iterator, Optional, Protocol, T_contra, TypeVar, Union
from random import random
from concurrent.futures import ThreadPoolExecutor

S_contra = TypeVar("S", contravariant=True)

@runtime_checkable
class LessThan(Protocol[S_contra, T_contra]):
    def __lt__(self: S_contra, other: T_contra) -> bool:
        raise NotImplementedError

@runtime_checkable
class GreaterThan(Protocol[S_contra, T_contra]):
    def __gt__(self: S_contra, other: T_contra) -> bool:
        raise NotImplementedError

@runtime_checkable
class LessEqual(Protocol[S_contra, T_contra]):
    def __le__(self: S_contra, other: T_contra) -> bool:
        raise NotImplementedError

@runtime_checkable
class GreaterEqual(Protocol[S_contra, T_contra]):
    def __ge__(self: S_contra, other: T_contra) -> bool:
        raise NotImplementedError

Comparable = Union[LessThan, GreaterThan, LessEqual, GreaterEqual]

S = TypeVar("S", bound=Comparable)
T = TypeVar("T", bound=Comparable)


class TreapValues(Generic[T]):
    """View into the values of a treap."""
    root: Optional[TreapNode[T]]

    def __init__(self: TreapValues[T], root: Optional[TreapNode[T]]) -> None:
        """Store the root being viewed into."""
        self.root = root

    def __iter__(self: TreapValues[T]) -> Iterator[T]:
        """In-order traversal over the values."""
        return (node.value for node in (self.root or ()))

    def __reversed__(self: TreapValues[T]) -> Iterator[T]:
        """Reversed in-order traversal over the values."""
        return (node.value for node in reversed(self.root or ()))


class TreapNode(Generic[T]):
    """Treap Node class with recursive reference to all of the children."""
    value: T
    priority: float
    left: Optional[TreapNode[T]]
    right: Optional[TreapNode[T]]

    def __init__(self: TreapNode[T], value: T, priority: float = None, left: TreapNode[T] = None, right: TreapNode[T] = None) -> None:
        self.value = value
        self.priority = random() if priority is None else priority
        self.left = left
        self.right = right

    def __bool__(self: TreapNode[T]) -> bool:
        """Returns True since it has at least one node: itself."""
        return True

    def __contains__(self: TreapNode[T], value: T) -> bool:
        """Checks if a given value is in the treap."""
        return (
             value == self.value
             or (value < self.value and value in (self.left or ()))
             or (value > self.value and value in (self.right or ()))
        )

    def __iter__(self: TreapNode[T]) -> Iterator[TreapNode[T]]:
        """In-order traversal over the treap."""
        yield from (self.left or ())
        yield self
        yield from (self.right or ())

    def __reversed__(self: TreapNode[T]) -> Iterator[TreapNode[T]]:
        """Reversed in-order traversal over the treap."""
        yield from reversed(self.right or ())
        yield self
        yield from reversed(self.left or ())

    def __len__(self: TreapNode[T]) -> int:
        """Returns the number of nodes in the treap."""
        return 1 + len(self.left or ()) + len(self.right or ())

    def __repr__(self: TreapNode[T]) -> str:
        """String format of the treap as the constructor."""
        return f"{type(self).__name__}({repr(self.value)}, {self.priority}, {repr(self.left or 'None')}, {repr(self.right or 'None')})"

    def __str__(self: TreapNode[T]) -> str:
        """String format of the treap as a tree."""
        # Split strings by new lines.
        left_str = str(self.left or "").split("\n")
        right_str = str(self.right or "").split("\n")
        # Desired line lengths.
        left_length = len(left_str[0])
        right_length = len(right_str[0])
        # Find the root for the diagonal lines to stop at.
        left_root = left_str[1].rfind("\\") if len(left_str) > 1 else left_length // 2 + 1
        right_root = right_str[1].rfind("\\") if len(right_str) > 1 else right_length // 2
        # Prepend diagonal lines.
        left_str = [
            " " * (left_length - i - 1)
            + "/"
            + " " * i
            for i
            in range(left_length - left_root)
        ] + left_str
        right_str = [
            " " * i
            + "\\"
            + " " * (right_length - i - 1)
            for i
            in range(right_root - 1)
        ] + right_str
        # Pad with spaces.
        left_str += [" " * left_length] * (len(right_str) - len(left_str))
        right_str += [" " * right_length] * (len(left_str) - len(right_str))
        # return the following:
        #         root
        #         / \
        # left_str   right_str
        return "\n".join([
            (
                " " * (left_length - right_length)
                + str(self.value).center(2 * min(left_length, right_length) + 3)
                + " " * (right_length-left_length)
            ),
            " " * left_length + "/ \\" + " " * right_length,
        ] + [
            left_line + "   " + right_line
            for left_line, right_line
            in zip(left_str, right_str)
        ])

    def height(self: TreapNode[T]) -> int:
        """Returns the height of the treap."""
        return 1 + max(
            self.left.height() if self.left else 0,
            self.right.height() if self.right else 0,
        )

    def rotate_left(self: TreapNode[T]) -> TreapNode[T]:
        """
        Rotates the treap to the left.
        Is the reverse of the rotate_right method.
        
         self            R
         / \    --->    / \
        L   R        self  Y
           / \        / \
          X   Y      L   X
        
        Preserves binary tree property.
        Preserves all heap properties
        except for self and R, which get swapped.
        Returns the new root.
        """
        R = self.right
        X = R.left
        R.left = self
        self.right = X
        return R

    def rotate_right(self: TreapNode[T]) -> TreapNode[T]:
        """
        Rotates the treap to the right.
        Is the reverse of the rotate_left method.
        
           self        L
           / \  --->  / \
          L   R      X  self
         / \            / \
        X   Y          Y   R
        
        Preserves binary tree property.
        Preserves all heap properties
        except for self and L, which get swapped.
        Returns the new root.
        """
        L = self.left
        Y = L.right
        L.right = self
        self.left = Y
        return L

    def insert(self: TreapNode[T], node: TreapNode[T]) -> TreapNode[T]:
        """Insert a new node and return the root."""
        # Insert onto left if node.value is less.
        if node.value < self.value:
            self.left = self.left.insert(node) if self.left else node
            if self.left.priority < self.priority:
                self = self.rotate_right()
        # Insert onto the right if node.value is greater than or equal to.
        else:
            self.right = self.right.insert(node) if self.right else node
            if self.right.priority < self.priority:
                self = self.rotate_left()
        # Return the new root.
        return self

    def search(self: TreapNode[T], value: T) -> TreapNode[T]:
        """
        Returns the first node with the matching value.

        Raises ValueError if the value is not present.
        """
        # Node is found.
        if value == self.value:
            return self
        # Node is on the left.
        elif value < self.value and self.left:
            return self.left.search(value)
        # Node is on the right.
        elif value > self.value and self.right:
            return self.right.search(value)
        # value not found.
        raise ValueError(f"{value} not in treap")

    def delete(self: TreapNode[T], value: T) -> Optional[TreapNode[T]]:
        """
        Deletes the first occurrence of a node with the given value.
        Returns the new root.
        Raises ValueError if the value is not present.
        """
        # Node not found.
        if not self.left and value < self.value or not self.right and value > self.value:
            raise ValueError(f"{value} not in treap")
        # Node is on the left.
        elif value < self.value:
            self.left = self.left.delete(value)
        # Node is on the right.
        elif value > self.value:
            self.right = self.right.delete(value)
        # Node is found.
        # Nothing on the left, replace by the right.
        elif not self.left:
            self = self.right
        # Nothing on the right, replace by the left.
        elif not self.right:
            self = self.left
        # Should be replaced by the left.
        elif self.left.priority < self.right.priority:
            self = self.rotate_right()
            self.right = self.right.delete(value)
        # Should be replaced by the right.
        else:
            self = self.rotate_left()
            self.left = self.left.delete(value)
        # Return the root.
        return self

    def max_(self: TreapNode[T]) -> TreapNode[T]:
        """Returns the maximum node in the treap."""
        return next(reversed(self))

    def min_(self: TreapNode[T]) -> TreapNode[T]:
        """Returns the minimum node in the treap."""
        return next(iter(self))

    def copy(self: TreapNode[T]) -> TreapNode[T]:
        """Returns a shallow copy of the entire treap."""
        return type(self)(
            self.value,
            self.priority,
            self.left.copy() if self.left else None,
            self.right.copy() if self.right else None,
        )

    def values(self: TreapNode[T]) -> TreapValues[T]:
        """Generates all values in the treap."""
        return TreapValues(self)


class Treap(Generic[T]):
    """Treap class with reference to the root node."""
    root: Optional[TreapNode[T]]

    def __init__(self: Treap[T], iterable: Iterable[T] = (), /, *, root: TreapNode[T] = None) -> None:
        """Create a treap given an iterable. By default, an empty treap is used."""
        # Initialize the root.
        self.root = root
        # Loop through the iterable.
        it = iter(iterable)
        # Create a unique object to test for stopping the loop.
        stop = object()
        # Get the first value.
        x = next(it, stop)
        # Get the next value and insert the previous value into the treap concurrently.
        with ThreadPoolExecutor(max_workers=2) as executor:
            while x is not stop:
                f_insert = executor.submit(self.insert, x)
                f_next = executor.submit(next, it, stop)
                f_insert.result()
                x = f_next.result()

    def __bool__(self: Treap[T]) -> bool:
        """Returns if the treap has any nodes."""
        return bool(self.root)

    def __contains__(self: Treap[T], value: T) -> bool:
        """Checks if a value is in the treap."""
        return value in (self.root or ())

    def __iter__(self: Treap[T]) -> Iterator[TreapNode[T]]:
        """In-order traversal over the treap."""
        return iter(self.root or ())

    def __reversed__(self: Treap[T]) -> Iterator[TreapNode[T]]:
        """Reversed in-order traversal over the treap."""
        return reversed(self.root or ())

    def __len__(self: Treap[T]) -> int:
        """Returns the number of nodes in the treap."""
        return len(self.root or ())

    def __repr__(self: Treap[T]) -> str:
        """String format of the treap as the constructor."""
        return f"{type(self).__name__}({list(self.values())})"

    def __str__(self: Treap[T]) -> str:
        """String format of the treap as a tree."""
        return str(self.root or "")

    def height(self: Treap[T]) -> int:
        """Returns the height of the treap."""
        return self.root.height() if self.root else 0

    def insert(self: Treap[T], value: T) -> None:
        """Insert a node into the treap."""
        self.root = self.root.insert(TreapNode(value)) if self.root else TreapNode(value)

    def search(self: Treap[T], value: T) -> TreapNode[T]:
        """
        Returns the first node with the matching value.

        Raises ValueError if the value is not present.
        """
        if not self.root:
            raise ValueError(f"{value} not in treap")
        return self.root.search(value)

    def delete(self: Treap[T], value: T) -> None:
        """
        Deletes the first occurrence of a node with the given value.
        Returns the new root.

        Raises ValueError if the value is not present.
        """
        if not self.root:
            raise ValueError(f"{value} not in treap")
        self.root = self.root.delete(value)

    def max_(self: Treap[T]) -> TreapNode[T]:
        """Returns the maximum node in the treap."""
        if self.root:
            return self.root.max_()
        raise ValueError("empty treap has no max")

    def min_(self: Treap[T]) -> TreapNode[T]:
        """Returns the minimum node in the treap."""
        if self.root:
            return self.root.min_()
        raise ValueError("empty treap has no min")

    def copy(self: TreapNode[T]) -> TreapNode[T]:
        """Returns a shallow copy of the entire treap."""
        return type(self)(self.values())

    def values(self: TreapNode[T]) -> Iterator[T]:
        """Generates all values in the treap."""
        return TreapValues(self.root)


def treap_sort(iterable: Iterable[T], /, *, key: Callable[[T], S] = None, reverse: bool = False) -> Iterator[T]:
    """
    Sorts using heap sort. This allows results to be sorted as they are received.
    This is useful if iterating through is slow so the results may be sorted while waiting.

    key and reverse are the same parameters from the built-in sort. Sorting is also stable, so it
    preserves the original order when elements are equal.
    """
    if key is None and reverse:
        return (v for v, i in reversed(Treap((v, -i) for i, v in enumerate(iterable)).values()))
    elif key is None:
        return iter(Treap(iterable).values())
    elif reverse:
        return (v for k, i, v in reversed(Treap((key(v), -i, v) for i, v in enumerate(iterable)).values()))
    else:
        return (v for k, i, v in Treap((key(v), i, v) for i, v in enumerate(iterable)).values())
