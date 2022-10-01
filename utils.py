def load_txt_one_line(path: str) -> str:
    """txt の 1 行目を返す"""
    f = open(path, "r")
    return f.readline().rstrip("\n")


def line_slice(line: str, prefix: str, suffix: str) -> str:
    """文字列 line の (最も左の) prefix と (その直後の) suffix に挟まれている文字列を切り出す"""
    slice_start_ind = line.index(prefix) + len(prefix)
    slice_end_ind = line.index(suffix, slice_start_ind)
    return line[slice_start_ind:slice_end_ind]
