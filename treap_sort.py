"""
Implementation of treap sort to sort results as they are received.

>>> print(*treap_sort([1, 7, 8, 0, 4, 6, 2, 3, 5]))
0 1 2 3 4 5 6 7 8
"""
from __future__ import annotations
from typing import runtime_checkable, Generic, Iterable, Iterator, Optional, Protocol, T_contra, TypeVar, Union
from random import random
from concurrent.futures import ThreadPoolExecutor
from itertools import zip_longest

S_contra = TypeVar("S_contra", contravariant=True)

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
    """Treap Node class with recursive reference to all of the subtreaps."""
    __slots__ = ["value", "priority", "left", "right"]
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

    def __lt__(self: Optional[TreapNode[T]], other: Optional[TreapNode[T]]) -> bool:
        """Returns if self is contained by other but has different unique elements."""
        return self.copy().unique() != other.copy().unique() and self <= other

    def __le__(self: Optional[TreapNode[T]], other: Optional[TreapNode[T]]) -> bool:
        """Returns if self is contained by other."""
        return not (self.copy() - other)

    def __eq__(self: Optional[TreapNode[T]], other: Optional[TreapNode[T]]) -> bool:
        """Returns if two treaps have the same values."""
        # Check in-order traversal over values.
        return all(s == o for s, o in zip_longest((self or {}).values(), (other or {}).values(), fillvalue=object()))

    def __ne__(self: Optional[TreapNode[T]], other: Optional[TreapNode[T]]) -> bool:
        """Returns if two treaps have any different values."""
        # Check in-order traversal over values.
        return any(s != o for s, o in zip_longest((self or {}).values(), (other or {}).values(), fillvalue=object()))

    def __gt__(self: Optional[TreapNode[T]], other: Optional[TreapNode[T]]) -> bool:
        """Returns if self contains other but has different unique elements."""
        return self.copy().unique() != other.copy().unique() and self >= other

    def __ge__(self: Optional[TreapNode[T]], other: Optional[TreapNode[T]]) -> bool:
        """Returns if self contains other."""
        return not (other.copy() - self)

    def __add__(self: Optional[TreapNode[T]], other: Optional[TreapNode[T]]) -> Optional[TreapNode[T]]:
        """Combines two treaps, destructively, keeping all nodes from both treaps, and returns the new treap."""
        # If either treap is empty, return the treap which is not, or None.
        if not self or not other:
            return self or other
        elif self.priority < other.priority:
            left, right = other.split(self.value)
            return type(self)(self.value, self.priority, type(self).__add__(self.left, left), type(self).__add__(self.right, right))
        else:
            left, right = self.split(other.value)
            return type(self)(other.value, other.priority, type(self).__add__(left, other.left), type(self).__add__(right, other.right))

    def __sub__(self: Optional[TreapNode[T]], other: Optional[TreapNode[T]]) -> Optional[TreapNode[T]]:
        """Returns a new treap using values from self but not from other. Destructively modifies self but not other."""
        # Nothing to remove if one of them is empty.
        if not self or not other:
            return self
        # Delete other's value from self.
        self = self.delete_all(other.value)
        # Nothing to remove if its now empty.
        if not self:
            return self
        # Split and remove from the left and right subtreaps.
        left, right = self.split(other.value)
        left = left and left - other.left
        right = right and right - other.right
        # Rejoin the two subtreaps using the split value.
        root = type(self)(other.value, 0.0, left, right)
        return root.delete_node(root)

    def __or__(self: Optional[TreapNode[T]], other: Optional[TreapNode[T]]) -> Optional[TreapNode[T]]:
        """
        Combines two treaps, destructively, keeping unique
        nodes from both treaps, and returns the new treap.
        """
        # If either treap is empty, return the treap which is not, or None.
        if not self or not other:
            return self and self.unique() or other and other.unique()
        # If self has priority, split other.
        elif self.priority < other.priority:
            # Remove duplicates.
            self = self.delete_all_except(self.value)
            if self.value in other:
                other = other.delete_all(self.value)
            # Nothing to split, done.
            if not other:
                return self
            # Split along the the root value.
            left, right = other.split(self.value)
            # Create a new root using the combined left and right sides of the root.
            return type(self)(self.value, self.priority, type(self).__or__(self.left, left), type(self).__or__(self.right, right))
        # If other has priority, split self.
        else:
            # Remove duplicates.
            other = other.delete_all_except(other.value)
            if other.value in self:
                self = self.delete_all(other.value)
            # Nothing to split, done.
            if not self:
                return other
            # Split along the the root value.
            left, right = self.split(other.value)
            # Create a new root using the combined left and right sides of the root.
            return type(self)(other.value, other.priority, type(self).__or__(left, other.left), type(self).__or__(right, other.right))

    def __and__(self: Optional[TreapNode[T]], other: Optional[TreapNode[T]]) -> Optional[TreapNode[T]]:
        """
        Combines two treaps, destructively, keeping only unique nodes
        which appears in both treaps, and return the new treap.
        """
        # If either treap is empty, there are no shared values.
        if not self or not other:
            return None
        # If self has priority, split other.
        elif self.priority < other.priority:
            # Check for duplicates.
            in_both = self.value in other
            # Remove duplicates.
            self = self.delete_all_except(self.value)
            if in_both:
                other = other.delete_all(self.value)
            # Nothing to split, done.
            if not other:
                return self
            # Split and join the subtreaps.
            left, right = other.split(self.value)
            self.left = type(self).__and__(self.left, left)
            self.right = type(self).__and__(self.right, right)
            # Remove non-duplicates.
            if not in_both:
                self = self.delete(self.value)
            return self
        # If other has priority, split self.
        else:
            # Check for duplicates.
            in_both = other.value in self
            # Remove duplicates.
            other = other.delete_all_except(other.value)
            if in_both:
                self = self.delete_all(other.value)
            # Nothing to split, done.
            if not self:
                return other
            # Split and join the subtreaps.
            left, right = self.split(other.value)
            other.left = type(self).__and__(left, other.left)
            other.right = type(self).__and__(right, other.right)
            # Remove non-duplicates.
            if not in_both:
                other = other.delete(other.value)
            return other

    def __xor__(self: Optional[TreapNode[T]], other: Optional[TreapNode[T]]) -> Optional[TreapNode[T]]:
        """
        Combines two treaps, destructively, keeping only unique nodes
        which appear in only one treap, and returns the new treap.
        """
        # If either treap is empty, return the treap which is not, or None.
        if not self or not other:
            return self and self.unique() or other and other.unique()
        # If self has priority, split other.
        elif self.priority < other.priority:
            # Check for duplicates.
            in_both = self.value in other
            # Remove duplicates.
            other = other.delete_all(self.value)
            # Nothing to split, done.
            if not other:
                return self.delete_all(self.value)
            # Split and join the subtreaps.
            left, right = other.split(self.value)
            self.left = type(self).__xor__(self.left, left)
            self.right = type(self).__xor__(self.right, right)
            # Remove duplicates.
            return self.delete_all(self.value) if in_both else self.delete_all_except(self.value)
        # If other has priority, split self.
        else:
            # Check for duplicates.
            in_both = other.value in self
            # Remove duplicates.
            self = self.delete_all(other.value)
            # Nothing to split, done.
            if not self:
                return other.delete_all(other.value)
            # Split and join the subtreaps.
            left, right = self.split(other.value)
            other.left = type(self).__xor__(left, other.left)
            other.right = type(self).__xor__(right, other.right)
            # Remove duplicates.
            return other.delete_all(other.value) if in_both else other.delete_all_except(other.value)

    def issubset(self: Optional[TreapNode[T]], other: Optional[TreapNode[T]]) -> bool:
        """Returns if self is a subset of other."""
        return self is None or self <= other

    def issuperset(self: Optional[TreapNode[T]], other: Optional[TreapNode[T]]) -> bool:
        """Returns if self is a superset of other."""
        return other is None or other <= self

    def isdisjoint(self: Optional[TreapNode[T]], other: Optional[TreapNode[T]]) -> bool:
        """Returns if self and other share no values."""
        # Emptry treaps are disjoint.
        if not self or not other:
            return True
        # Randomly choose which root to use.
        if random() < 0.5:
            self, other = other, self
        # They share a value.
        if self.value in other:
            return False
        # Split and compare subtreaps.
        left, right = other.split(self.value)
        return type(self).isdisjoint(self.left, left) and type(self).isdisjoint(self.right, right)

    def unique(self: TreapNode[T]) -> TreapNode[T]:
        """Deletes all duplicate occurrences of any value."""
        self = self.delete_all_except(self.value)
        self.left = self.left and self.left.unique()
        self.right = self.right and self.right.unique()
        return self

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

    def add(self: TreapNode[T], value: T, *args, **kwargs) -> TreapNode[T]:
        """Add a new value if its not already in the treap and return the root."""
        # Insert onto left if the value is less.
        if value < self.value:
            self.left = self.left.add(value, *args, **kwargs) if self.left else type(self)(value, *args, **kwargs)
            if self.left.priority < self.priority:
                self = self.rotate_right()
        # Insert onto the right if the value is greater.
        elif value > self.value:
            self.right = self.right.add(value, *args, **kwargs) if self.right else type(self)(value, *args, **kwargs)
            if self.right.priority < self.priority:
                self = self.rotate_left()
        # Do nothing if value == self.value.
        # Return the new root.
        return self

    def insert(self: TreapNode[T], value: T, *args, **kwargs) -> TreapNode[T]:
        """Insert a new value and return the root."""
        # Insert onto left if the value is less.
        if value < self.value:
            self.left = self.left.insert(value, *args, **kwargs) if self.left else type(self)(value, *args, **kwargs)
            if self.left.priority < self.priority:
                self = self.rotate_right()
        # Insert onto the right if the value is greater than or equal to (for stable sorting).
        else:
            self.right = self.right.insert(value, *args, **kwargs) if self.right else type(self)(value, *args, **kwargs)
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

    def delete_all(self: TreapNode[T], value: T) -> Optional[TreapNode[T]]:
        """Deletes all occurrences of the value in the treap."""
        while value in (self or ()):
            self = self.delete(value)
        return self

    def delete_all_except(self: TreapNode[T], value: T) -> TreapNode[T]:
        """Deletes all but one occurrences of the value in the treap."""
        try:
            first = self.search(value)
        except ValueError:
            return self
        if first.left:
            first.left = first.left.delete_all(value)
        if first.right:
            first.right = first.right.delete_all(value)
        return self

    def delete_node(self: TreapNode[T], node: TreapNode[T]) -> TreapNode[T]:
        """
        Deletes the provided node, replacing `==` with `is`.
        Returns the new root.

        Raises ValueError if the node is not present.
        """
        # Node not found.
        if not self.left and node.value < self.value or not self.right and node.value > self.value:
            raise ValueError("node not in treap")
        # Node is on the left.
        elif node.value < self.value:
            self.left = self.left.delete_node(node)
        # Node is on the right.
        elif node.value > self.value:
            self.right = self.right.delete_node(node)
        # Node is not found, but the value is equal.
        elif node is not self:
            # Check each side.
            if self.left and node.value == self.left.value:
                try:
                    self.left = self.left.delete_node(node)
                except ValueError:
                    pass
                else:
                    return self
            if self.right and node.value == self.right.value:
                try:
                    self.right = self.right.delete_node(node)
                except ValueError:
                    pass
                else:
                    return self
            # Node still not found.
            raise ValueError("node not in treap")
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
            self.right = self.right.delete_node(node)
        # Should be replaced by the right.
        else:
            self = self.rotate_left()
            self.left = self.left.delete_node(node)
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
            self.left and self.left.copy(),
            self.right and self.right.copy(),
        )

    def nodes(self: TreapNode[T]) -> Iterator[TreapNode[T]]:
        """Generates all nodes in the treap."""
        return iter(self)

    def values(self: TreapNode[T]) -> TreapValues[T]:
        """Generates all values in the treap."""
        return TreapValues(self)

    def split(self: TreapNode[T], value: T) -> tuple[Optional[TreapNode[T]], Optional[TreapNode[T]]]:
        """Split a treap along a value, destructively. Return the left and right subtreaps."""
        # Insert the new value and force its priority to make it become the root.
        self = self.insert(value, 0.0)
        # Return the left and right subtreaps.
        return self.left, self.right

    def join(self: Optional[TreapNode[T]], other: Optional[TreapNode[T]]) -> TreapNode[T]:
        """
        Combines two treaps destructively. Returns the new treap.

        Assumes `self.max_().value <= other.min_().value`, or one of them must be empty.
        """
        # If either treap is empty, return the treap which is not, or None.
        if not self or not other:
            return self or other
        # Insert the new value as the root.
        self = type(self)(self.max_().value, 0.0, self, other)
        # Return the new treap after we delete this node.
        return self.delete_node(self)


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

    def __iter__(self: Treap[T]) -> Iterator[T]:
        """In-order traversal over the treap values."""
        return iter(TreapValues(self.root))

    def __reversed__(self: Treap[T]) -> Iterator[T]:
        """Reversed in-order traversal over the treap."""
        return reversed(TreapValues(self.root))

    def __len__(self: Treap[T]) -> int:
        """Returns the number of nodes in the treap."""
        return len(self.root or ())

    def __repr__(self: Treap[T]) -> str:
        """String format of the treap as the constructor."""
        return f"{type(self).__name__}({list(self)})"

    def __str__(self: Treap[T]) -> str:
        """String format of the treap as a tree."""
        return str(self.root or "")

    def __lt__(self: Treap[T], other: Treap[T]) -> bool:
        """Returns if self is contained other but has different unique elements."""
        return TreapNode.__lt__(self.root, other.root)

    def __le__(self: Treap[T], other: Treap[T]) -> bool:
        """Returns if self is contained by other."""
        return TreapNode.__le__(self.root, other.root)

    def __eq__(self: Treap[T], other: Treap[T]) -> bool:
        """Returns if two treaps have all same values."""
        return TreapNode.__eq__(self.root, other.root)

    def __ne__(self: Treap[T], other: Treap[T]) -> bool:
        """Returns if two treaps have any different values."""
        return TreapNode.__ne__(self.root, other.root)

    def __gt__(self: Treap[T], other: Treap[T]) -> bool:
        """Returns if self contains other but has different unique elements."""
        return TreapNode.__gt__(self.root, other.root)

    def __ge__(self: Treap[T], other: Treap[T]) -> bool:
        """Returns if self contains other."""
        return TreapNode.__ge__(self.root, other.root)

    def __add__(self: Treap[T], other: Treap[T]) -> Treap[T]:
        """Combines two treaps, in-destructively, keeping all nodes from both treaps, and returns the new treap."""
        return type(self)(root=TreapNode.__add__(self.copy().root, other.copy().root))

    def __iadd__(self: Treap[T], other: Treap[T]) -> Treap[T]:
        """Combines two treaps, in-place, without editing the other treap, keeping all nodes from both treaps, and returns the new treap."""
        self.root = TreapNode.__add__(self.root, other.copy().root)
        return self

    def __sub__(self: Treap[T], other: Treap[T]) -> Treap[T]:
        """Returns a new treap using values from self but not from other."""
        return type(self)(root=TreapNode.__sub__(self.copy().root, other.root))

    def __isub__(self: Treap[T], other: Treap[T]) -> Treap[T]:
        """Subtracts two treaps, in-place, using values from self but not from other."""
        self.root = TreapNode.__sub__(self.root, other.root)
        return self

    def __or__(self: Treap[T], other: Treap[T]) -> Treap[T]:
        """Combines two treaps, in-destructively, keeping unique nodes from both treaps, and returns the new treap."""
        return type(self)(root=TreapNode.__or__(self.copy().root, other.copy().root))

    def __ior__(self: Treap[T], other: Treap[T]) -> Treap[T]:
        """Combines two treaps, in-place, without editing the other treap, keeping unique nodes from both treaps, and returns the new treap."""
        self.root = TreapNode.__or__(self.root, other.copy().root)
        return self

    def __and__(self: Treap[T], other: Treap[T]) -> Treap[T]:
        """Combines two treaps, in-destructively, keeping only nodes which appears in both treaps, and returns the new treap."""
        return type(self)(root=TreapNode.__and__(self.copy().root, other.copy().root))

    def __iand__(self: Treap[T], other: Treap[T]) -> Treap[T]:
        """Combines two treaps, in-place, without editing the other treap, keeping only nodes which appears in both treaps, and returns the new treap."""
        self.root = TreapNode.__and__(self.root, other.copy().root)
        return self

    def __xor__(self: Treap[T], other: Treap[T]) -> Treap[T]:
        """Combines two treaps, in-destructively, keeping only nodes which appears in one treap, and returns the new treap."""
        return type(self)(root=TreapNode.__xor__(self.copy().root, other.copy().root))

    def __ixor__(self: Treap[T], other: Treap[T]) -> Treap[T]:
        """Combines two treaps, in-place, without editing the other treap, keeping only nodes which appears in one treap, and returns the new treap."""
        self.root = TreapNode.__xor__(self.root, other.copy().root)
        return self

    def issubset(self: Treap[T], other: Treap[T]) -> bool:
        """Returns if self is a subset of other. Equivalent to self <= other."""
        return self <= other

    def issuperset(self: Treap[T], other: Treap[T]) -> bool:
        """Returns if self is a superset of other. Equivalent to self >= other."""
        return self >= other

    def isdisjoint(self: Treap[T], other: Treap[T]) -> bool:
        """Returns if self and other share no values."""
        return not self or not other or self.root.isdisjoint(other.root)

    def unique(self: Treap[T]) -> Treap[T]:
        """Deletes all duplicate occurrences of any value."""
        self.root = self.root and self.root.unique()
        return self

    def extend(self: Treap[T], other: Treap[T]) -> Treap[T]:
        """
        Combines two treaps, in-destructively, keeping all nodes from both treaps, and returns the new treap.

        Equivalent to self + other.
        """
        return self + other

    def difference(self: Treap[T], other: Treap[T]) -> Treap[T]:
        """
        Returns a new treap using values from self but not from other.

        Equivalent to self - other.
        """
        return self - other

    def union(self: Treap[T], other: Treap[T]) -> Treap[T]:
        """
        Combines two treaps, in-destructively, keeping unique nodes from both treaps, and returns the new treap.

        Equivalent to self | other.
        """
        return self | other

    def intersection(self: Treap[T], other: Treap[T]) -> Treap[T]:
        """
        Combines two treaps, in-destructively, keeping only nodes which appears in both treaps, and returns the new treap.

        Equivalent to self & other.
        """
        return self & other

    def symmetric_difference(self: Treap[T], other: Treap[T]) -> Treap[T]:
        """
        Combines two treaps, in-destructively, keeping only nodes which appears in one treap, and returns the new treap.

        Equivalent to self ^ other.
        """
        return self ^ other

    def height(self: Treap[T]) -> int:
        """Returns the height of the treap."""
        return self.root.height() if self else 0

    def add(self: Treap[T], value: T, *args, **kwargs) -> None:
        """Add a value into the treap if its not already in the treap."""
        self.root = self.root.add(value, *args, **kwargs) if self else TreapNode(value, *args, **kwargs)

    def insert(self: Treap[T], value: T, *args, **kwargs) -> None:
        """Insert a value into the treap."""
        self.root = self.root.insert(value, *args, **kwargs) if self else TreapNode(value, *args, **kwargs)

    def search(self: Treap[T], value: T) -> TreapNode[T]:
        """
        Returns the first node with the matching value.

        Raises ValueError if the value is not present.
        """
        if self.root:
            return self.root.search(value)
        raise ValueError(f"{value} not in treap")

    def delete(self: Treap[T], value: T) -> None:
        """
        Deletes the first occurrence of a node with the given value.
        Returns the new root.

        Raises ValueError if the value is not present.
        """
        if self:
            self.root = self.root.delete(value)
        raise ValueError(f"{value} not in treap")

    def max_(self: Treap[T]) -> TreapNode[T]:
        """Returns the maximum node in the treap."""
        if self:
            return self.root.max_()
        raise ValueError("empty treap has no max")

    def min_(self: Treap[T]) -> TreapNode[T]:
        """Returns the minimum node in the treap."""
        if self:
            return self.root.min_()
        raise ValueError("empty treap has no min")

    def copy(self: Treap[T]) -> Treap[T]:
        """Returns a shallow copy of the entire treap."""
        return type(self)(root=(self.root and self.root.copy()))

    def nodes(self: Treap[T]) -> Iterator[TreapNode[T]]:
        """Generates all nodes in the treap."""
        return iter(self.root)

    def values(self: Treap[T]) -> TreapValues[T]:
        """Generates all values in the treap."""
        return TreapValues(self.root)


class OrderedSet(Generic[T], Treap[T]):
    """Implementation of an ordered set using the treap data structure."""

    def __add__(self: OrderedSet[T], other: OrderedSet[T]) -> OrderedSet[T]:
        """Combines two treaps, in-destructively, keeping unique nodes from both treaps, and returns the new treap."""
        return type(self)(root=TreapNode.__or__(self.root.copy(), other.root.copy()))

    def __iadd__(self: OrderedSet[T], other: OrderedSet[T]) -> OrderedSet[T]:
        """Combines two treaps, in-place, without editing the other treap, keeping unique nodes from both treaps, and returns the new treap."""
        self.root = TreapNode.__or__(self.root, other.root.copy())
        return self

    def unique(self: OrderedSet[T]) -> OrderedSet[T]:
        """Deletes all duplicate occurrences of any value. Returns self without modification."""
        return self

    def insert(self: OrderedSet[T], value: T, *args, **kwargs) -> None:
        """Add a value into the treap if its not already in the treap. Equivalent to self.add(...)."""
        self.root = self.root.add(value, *args, **kwargs) if self else TreapNode(value, *args, **kwargs)

    def extend(self: OrderedSet[T], other: OrderedSet[T]) -> OrderedSet[T]:
        """
        Combines two treaps, in-destructively, keeping unique nodes from both treaps, and returns the new treap.

        Equivalent to self | other.
        """
        return self | other


def treap_sort(iterable: Iterable[T], /, *, key: Callable[[T], Comparable] = None, reverse: bool = False) -> Iterator[T]:
    """
    Sorts using heap sort. This allows results to be sorted as they are received.
    This is useful if iterating through is slow so the results may be sorted while waiting.

    key and reverse are the same parameters from the built-in sort. Sorting is also stable, so it
    preserves the original order when elements are equal.
    """
    if key is None and reverse:
        return (v for v, i in reversed(Treap((v, -i) for i, v in enumerate(iterable))))
    elif key is None:
        return iter(Treap(iterable))
    elif reverse:
        return (v for k, i, v in reversed(Treap((key(v), -i, v) for i, v in enumerate(iterable))))
    else:
        return (v for k, i, v in Treap((key(v), i, v) for i, v in enumerate(iterable)))
