# users_hogehoge.txtの各ユーザーの(補正を取ったrating, 早解き度)を（早解き度はprint_type.pyの要領で）まとめてnumpy配列に出力する。
# 1995年のみの補正を取っていないrating版は「rate_per_1995_レートの補正をとっていない.npy」として保存。

import time

import numpy as np

from print_type import get_type
from utils import rate_3_to_2, rate_4_to_3

f = open("ignore/analysis_1995/users_5n_and_top_20220829.txt", "r")
L = []
for item in f.readlines():
    user_name, rate4, times = item.split()
    rate2 = rate_3_to_2(rate_4_to_3(int(rate4)), int(times))
    per0, per1 = get_type(user_name)
    time.sleep(1)
    L.append([rate2, per0, per1])
    print(rate2, per0, per1, user_name)

f.close()

N = np.zeros((len(L), 3))
for i in range(len(L)):
    for j in range(3):
        N[i][j] = L[i][j]

np.save("analysis_1995/users_5n_and_top_20220829.npy", N)
