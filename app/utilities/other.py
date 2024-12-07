def split_list(lst: list, n: int):
    return [lst[i:i + n] for i in range(0, len(lst), n)]