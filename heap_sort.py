"""
Implementation of heap sort to produce results quickly.

>>> print(*heap_sort([1, 7, 8, 0, 4, 6, 2, 3, 5]))
0 1 2 3 4 5 6 7 8
"""
from __future__ import annotations
from typing import Iterable, Iterator, TypeVar
from heapq import heapify, heappop, _heapify_max as heapify_max, _heappop_max as heappop_max
from treap_sort import S, T

def heap_sort(x: Iterable[T], /, *, key: Callable[[T], S] = None, reverse: bool = False) -> Iterator[T]:
    """
    Sorts using heap sort. This allows results to be sent in sorted order quickly.
    This is useful if processing each result is slow so the results are needed as soon as possible.
    Another application is if only the first few results are wanted and a full sort is unnecessary.

    key and reverse are the same parameters from the built-in sort. Sorting is also stable, so it
    preserves the original order when elements are equal.
    """
    # Select appropriate heapq functions.
    if reverse:
        heapify_ = heapify_max
        heappop_1 = heappop_max
    else:
        heapify_ = heapify
        heappop_1 = heappop
    # Store keys and indexes with the values in a list.
    if key is None:
        x = [(v, -i if reverse else i) for i, v in enumerate(x)]
        heappop_2 = lambda x: heappop_1(x)[0]
    else:
        x = [(key(v), -i if reverse else i, v) for i, v in enumerate(x)]
        heappop_2 = lambda x: heappop_1(x)[2]
    # Apply heap sort.
    heapify_(x)
    for _ in range(len(x)):
        yield heappop_2(x)
