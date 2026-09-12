from pathlib import Path

import numpy as np

from .atcoder_client import AtCoderClient
from .print_type import Calc
from .utils import rate_3_to_2, rate_4_to_3


def make_output_file_path(file_name: str) -> str:
    """保存先ファイルパスを決める。重複時は連番を付ける。"""
    if not file_name.endswith(".npy"):
        file_name += ".npy"

    base_file_path = Path("data/hoseichi") / file_name
    candidate_file_path = base_file_path
    index = 1
    while candidate_file_path.is_file():
        candidate_file_path = base_file_path.with_name(f"{base_file_path.stem}_{index}{base_file_path.suffix}")
        index += 1

    return str(candidate_file_path)


def get_type_for_hosei(
    data: list[tuple[str, int, int]],
    file_name: str,
    client: AtCoderClient | None = None,
) -> str:
    """
    補正値作成に使うユーザー一覧から、
    (内部レート, 平均順位率, 重み付き平均順位率) の一覧を作って保存する。
    """
    file_path = make_output_file_path(file_name)

    calc = Calc(client=client)
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
        if n_contest_for_calc > 0:
            data_save.append([rate2, mean_rank_rate, weighted_mean_rank_rate])

    np.save(file_path, np.array(data_save))
    print("get_type_for_hosei end")
    print(f"saved_hoseichi_file: {file_path}")
    return file_path
