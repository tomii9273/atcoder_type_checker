# ユーザー名を入力し、コンテスト成績表と、あらかじめ得た点数と順位範囲のデータを元に、早解き度を出力する。
# 現状、早解き度（早解きほど小さく、0に近い）が、レートの高い人ほど小さい数値になっている可能性あり。

import ast
import json
import urllib.request


class Calc:
    def __init__(self) -> None:
        f = open("points/points.txt", "r")
        for item in f.readlines():
            main_D = ast.literal_eval(item)
            break
        f.close()
        self.main_D = main_D

    def get_rank_rate(self, user_name):
        url = "https://atcoder.jp/users/{}/history/json".format(user_name)

        with urllib.request.urlopen(url) as res:
            html = res.read().decode("utf-8")
        # print(html)
        js = json.loads(html)

        sum_per = 0
        per_w = 0
        sum_w = 0
        cnt = 0
        for i in range(len(js)):
            rated = js[i]["IsRated"]
            contest_name = js[i]["ContestScreenName"][:6]
            rank = js[i]["Place"]
            # print(contest_name, rank)
            if rated and contest_name in self.main_D:
                V = list(self.main_D[contest_name].values())
                K = list(self.main_D[contest_name].keys())
                ind = 0
                while ind < len(V) and (not (V[ind][0] <= rank <= V[ind][1])):
                    ind += 1
                score = K[ind] if ind < len(K) else 0
                if score != 0 and V[ind][1] != V[ind][0]:
                    cnt += 1
                    per = (rank - V[ind][0]) / (V[ind][1] - V[ind][0])
                    per_w += rank - V[ind][0]
                    sum_w += V[ind][1] - V[ind][0]
                    sum_per += per
                    # print(contest_name, rank, score, per)
        if cnt == 0:
            return (0, 0, 0)
        per0 = sum_per / cnt
        per1 = per_w / sum_w
        return (per0, per1, cnt)
