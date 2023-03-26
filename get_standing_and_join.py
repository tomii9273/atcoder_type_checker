# 各コンテストの順位表jsonを取得し（ログイン（認証）する必要あり）、
# 得た順位表jsonから、各点数の順位範囲を求め、元のファイル（points/points.txt）
# の辞書に追加して同名で保存する。
# get_standing.pyとanalysis_standing.pyをつなげたような構造。

import ast
import codecs
import json
import time

import requests
from bs4 import BeautifulSoup

# パラメータここから
contest_names = (
    [f"abc{i:03}" for i in range(292, 296)]
    + [f"arc{i:03}" for i in range(158, 159)]
    + [f"agc{i:03}" for i in range(62, 62)]
)
# パラメータここまで

pw = input("Password?: ")

# 各コンテストの順位表jsonを取得
for contest_name in contest_names:
    print("start", contest_name)

    url = "https://atcoder.jp/login?continue=https%3A%2F%2Fatcoder.jp%2Fcontests%2F{}%2Fstandings%2Fjson".format(
        contest_name
    )
    session = requests.session()
    response = session.get(url)
    bs = BeautifulSoup(response.text, "html.parser")

    # クッキーとトークンを取得
    authenticity = bs.find(attrs={"name": "csrf_token"}).get("value")
    cookie = response.cookies

    # ログイン情報
    info = {"username": "Tomii9273", "password": pw, "csrf_token": authenticity}

    # URLを叩き、htmlを表示
    res = session.post(url, data=info, cookies=cookie)
    # print(res.text)

    time.sleep(1)
    f = codecs.open("raw_standings/{}.txt".format(contest_name), "w", "utf-8")
    f.write(res.text)
    f.close()


# 元のファイル（points/points.txt）をロード
f = open("points/points.txt", "r")
for item in f.readlines():
    main_D = ast.literal_eval(item)
    break
f.close()


# 得た順位表jsonから、各点数の順位範囲を求め、追加
for contest_name in contest_names:
    print("load", contest_name)
    D = {}
    f = codecs.open("raw_standings/{}.txt".format(contest_name), "r", "utf-8")
    for item in f.readlines():
        SD = json.loads(item)["StandingsData"]
    for i in range(len(SD)):
        rank = SD[i]["Rank"]
        score = SD[i]["TotalResult"]["Score"] // 100
        # print(rank, score)
        if score in D:
            D[score][0] = min(D[score][0], rank)
            D[score][1] = max(D[score][1], rank)
        else:
            D[score] = [rank, rank]

    main_D[contest_name] = D
    f.close()


# 保存
f = open("points/points.txt", "w")
f.write(str(main_D))
f.close()
