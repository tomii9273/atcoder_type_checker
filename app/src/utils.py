from math import log


def add_p(s: str) -> str:
    """paragraph タグを付ける"""
    return "<p>" + s + "</p>"


def add_b(s: str) -> str:
    """太字タグを付ける"""
    return "<b>" + s + "</b>"


def load_txt_one_line(path: str) -> str:
    """txt の 1 行目を返す"""
    f = open(path, "r")
    return f.readline().rstrip("\n")


def rate_4_to_3(rate4: int) -> float:
    """
    https://qiita.com/anqooqie/items/92005e337a0d2569bdbd の「レート（第四段階）」を「レート（第三段階）」に変換。
    レートをマイナスにしない補正を外す。
    「レート（第四段階）」は実際にはわからないので、AtCoderでの表示上のレート (四捨五入して整数にしたものである) を引数に使うことが多い。
    これが 0 だと計算できないので、その場合便宜上 0.1 としている。
    """
    assert rate4 >= 0
    rate = max(rate4, 0.1)
    if rate < 400:
        return 400 - 400 * log(400 / rate)
    return rate


def rate_3_to_2(rate3: float, n_contest_rated: int) -> float:
    """
    https://qiita.com/anqooqie/items/92005e337a0d2569bdbd の「レート（第三段階）」を「レート（第二段階）」に変換。
    参加回数が少ないことによる補正を外す。
    n_contest_rated: Rated 参加回数
    """
    assert n_contest_rated >= 1
    return rate3 + (((1 - 0.81**n_contest_rated) ** 0.5) / (1 - 0.9**n_contest_rated) - 1) * 1200 / (19**0.5 - 1)
