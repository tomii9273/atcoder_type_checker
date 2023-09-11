import os
import time

import numpy as np

from .print_type import Calc
from .utils import rate_3_to_2, rate_4_to_3


def get_type_for_hosei(data: list[tuple[str, int, int]], file_name: str) -> None:
    """
    補正に使用する (ユーザー名, 補正後 rating, rated 参加数) の一覧から、
    (内部レート (第二段階), 平均順位率, 重み付き平均順位率) の一覧を求め、保存する。
    上書きはしない。
    """
    if not file_name.endswith(".npy"):
        file_name += ".npy"
    file_path = f"data/hoseichi/{file_name}"

    calc = Calc()
    data_save = []
    print("get_type_for_hosei start")
    print(f"n_user: {len(data)}")
    for i in range(len(data)):
        if i % 100 == 0:
            print(f"{i} start")
        user_name, rate4, n_contest_rated = data[i]
        if n_contest_rated == 0:
            continue
        rate2 = rate_3_to_2(rate_4_to_3(rate4), n_contest_rated)
        (
            mean_rank_rate,
            weighted_mean_rank_rate,
            n_contest_for_calc,
            n_contest_rated_got,
            rate4_got,
        ) = calc.get_rank_rate(user_name)
        assert n_contest_rated == n_contest_rated_got
        assert n_contest_for_calc <= n_contest_rated
        assert rate4 == rate4_got
        time.sleep(1)
        if n_contest_for_calc > 0:
            data_save.append([rate2, mean_rank_rate, weighted_mean_rank_rate])

    if os.path.isfile(file_path):
        file_path = file_path.rstrip(".npy") + "_1" + ".npy"
    np.save(file_path, np.array(data_save))
    print("get_type_for_hosei end")
