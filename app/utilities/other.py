"""
This module contains utility functions that do not fit into any other category.
"""

def split_list(lst: list, n: int):
    """
    Split a list into sublists of length n.

    Args:
        lst (list): The list to split.
        n (int): The length of each sublist.

    Returns:
        list: A list of sublists.
    """
    return [lst[i : i + n] for i in range(0, len(lst), n)]
