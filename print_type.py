# ユーザー名を入力し、コンテスト成績表と、あらかじめ得た点数と順位範囲のデータを元に、早解き度を出力する。
# 現状、早解き度（早解きほど小さく、0に近い）が、レートの高い人ほど小さい数値になっている可能性あり。

import ast
import json
import urllib.request

f = open("points/points_361_files.txt", "r")
for item in f.readlines():
    main_D = ast.literal_eval(item)
    break
f.close()


def get_type(user_name):

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
        if rated and contest_name in main_D:
            V = list(main_D[contest_name].values())
            K = list(main_D[contest_name].keys())
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

    per0 = sum_per / cnt
    per1 = per_w / sum_w
    return (per0, per1)


if __name__ == "__main__":
    print(get_type(input()))
