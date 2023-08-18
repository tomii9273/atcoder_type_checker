# users_hogehoge.txtの各ユーザーの(補正を取ったrating, 早解き度)を（早解き度はprint_type.pyの要領で）まとめてnumpy配列に出力する。
# 1995年のみの補正を取っていないrating版は「rate_per_1995_レートの補正をとっていない.npy」として保存。

import os
import time

import numpy as np

from print_type import Calc
from utils import rate_3_to_2, rate_4_to_3


def get_type_for_hosei(Data, file_name):
    """
    補正に使用する (ユーザー名, 補正後 rating, rated 参加数) の一覧から、
    (内部レート (第二段階), 平均順位率, 重み付き平均順位率 (現在未使用)) の一覧を求め、保存する。
    上書きはしない。
    """
    if not file_name.endswith(".npy"):
        file_name += ".npy"
    file_path = f"analysis_1995/{file_name}"

    calc = Calc()
    L = []
    for i in range(len(Data)):
        user_name, rate4, times = Data[i][0], Data[i][1], Data[i][2]
        rate2 = rate_3_to_2(rate_4_to_3(int(rate4)), int(times))
        per0, per1, _, _ = calc.get_rank_rate(user_name)
        time.sleep(1)
        L.append([rate2, per0, per1])

    N = np.zeros((len(L), 3))
    for i in range(len(L)):
        for j in range(3):
            N[i][j] = L[i][j]

    if os.path.isfile(file_path):
        file_path = file_path.rstrip(".npy") + "_1" + ".npy"
    np.save(file_path, N)
