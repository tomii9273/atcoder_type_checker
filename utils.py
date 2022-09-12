def load_txt_one_line(path: str) -> str:
    """txt の 1 行目を返す"""
    f = open(path, "r")
    return f.readline().rstrip("\n")
