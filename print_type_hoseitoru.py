# ユーザー名を入力し、コンテスト成績表と、あらかじめ得た点数と順位範囲のデータを元に、早解き度を出力する。
# 早解き度（早解きほど小さく、0に近い）はレートと相関があるので、予測値（users_5n_and_top_20220829.npy より取得）との差を出力する。
# また、レートには補正を取ったものを使用する。
import ast
import json
import urllib.request
from math import log

import numpy as np

N = np.load("analysis_1995/rate_per_19x5.npy").T
a = np.polyfit(N[0], N[1], 2)
a = np.poly1d(a)
b = np.polyfit(N[0], N[1], 2)
b = np.poly1d(b)


def rate43(rate4):
    rate = max(rate4, 0.1)
    if rate < 400:
        return 400 - 400 * log(400 / rate)
    return rate


def rate32(rate3, times):
    return rate3 + (((1 - 0.81 ** times) ** 0.5) / (1 - 0.9 ** times) - 1) * 1200 / (19 ** 0.5 - 1)


f = open("points/points.txt", "r")
for item in f.readlines():
    main_D = ast.literal_eval(item)
    break
f.close()


def test(a):
    return 12


def get_type(user_name):

    url = "https://atcoder.jp/users/{}/history/json".format(user_name)

    with urllib.request.urlopen(url) as res:
        html = res.read().decode("utf-8")
    # print(html)
    js = json.loads(html)

    sum_per = 0
    per_w = 0
    sum_w = 0
    n_contest = 0  # 計算に使用したコンテスト数
    for i in range(len(js)):
        rated = js[i]["IsRated"]
        contest_name = js[i]["ContestScreenName"][:6]
        rank = js[i]["Place"]
        if rated and contest_name in main_D:
            V = list(main_D[contest_name].values())
            K = list(main_D[contest_name].keys())
            ind = 0
            while ind < len(V) and (not (V[ind][0] <= rank <= V[ind][1])):
                ind += 1
            score = K[ind] if ind < len(K) else 0
            if score != 0 and V[ind][1] != V[ind][0]:
                n_contest += 1
                per = (rank - V[ind][0]) / (V[ind][1] - V[ind][0])
                per_w += rank - V[ind][0]
                sum_w += V[ind][1] - V[ind][0]
                sum_per += per
                # print(contest_name, rank, score, per)

    if n_contest == 0:
        return 0, 0, 0, 0, 0

    per0 = sum_per / n_contest
    per1 = per_w / sum_w

    rate4 = js[-1]["NewRating"]
    rate2 = rate32(rate43(int(rate4)), n_contest)
    # print(rate4, rate2, cnt, times)

    per0s = per0 - a(rate2)
    per1s = per1 - b(rate2)

    # return (per0, per1, per0s, per1s)
    return per0s, rate2, n_contest, per0, a(rate2)


if __name__ == "__main__":
    print(get_type(input()))
