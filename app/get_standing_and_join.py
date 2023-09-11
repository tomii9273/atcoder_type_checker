#!/usr/bin/env python3

# 各コンテストの順位表 json を取得し (ログイン (認証) する必要あり)、
# 得た順位表 json から、各点数の順位範囲を求め、元のファイル (points/points.txt)
# の辞書に追加して同名で保存する。

import ast
import json
import re
import sys
import time
import urllib.request

import requests
from bs4 import BeautifulSoup
from src.const import MY_USER_ID

# 「過去のコンテスト」のページから、コンテスト名を取得 (1 ページのみ見る)
contest_names_page_1: set[str] = set()

url = "https://atcoder.jp/contests/archive"
with urllib.request.urlopen(url) as res:
    html_data = res.read().decode("utf-8")

bs = BeautifulSoup(html_data, "html.parser")

body_data = (
    bs.find("div", {"class": "table-responsive"})
    .find("table", {"class": "table table-default table-striped table-hover table-condensed table-bordered small"})
    .find("tbody")
)
contest_blocks = body_data.find_all("tr")
for block in contest_blocks:
    contest_name = block.find_all("td")[1].find("a", href=True)["href"].split("/")[-1]
    if re.fullmatch("a[brg]c[0-9]{3}", contest_name):
        contest_names_page_1.add(contest_name)

# 既に取得済のコンテストを除外
with open("data/points/points.txt", "r") as f:
    first_line = f.readline().strip()
    score_rank_data = ast.literal_eval(first_line)
    contest_names_exist = set(score_rank_data.keys())
    contest_names = sorted(list(contest_names_page_1 - contest_names_exist))

print(f"新たに順位表 json を取得するコンテストの名前一覧: {contest_names}")

if len(contest_names) == 0:
    sys.exit()

if len(sys.argv) >= 2:
    password = sys.argv[1]  # GitHub Actions での実行の場合
else:
    password = input("Password?: ")  # 手動実行の場合

# 各コンテストのデータを取得・追加
for contest_name in contest_names:
    print("start", contest_name)

    # クッキーとトークンを取得
    url = f"https://atcoder.jp/login?continue=https%3A%2F%2Fatcoder.jp%2Fcontests%2F{contest_name}%2Fstandings%2Fjson"
    session = requests.session()
    response = session.get(url)
    bs = BeautifulSoup(response.text, "html.parser")

    authenticity = bs.find(attrs={"name": "csrf_token"}).get("value")
    cookie = response.cookies

    # ログインして順位表 json を取得
    info = {"username": MY_USER_ID, "password": password, "csrf_token": authenticity}
    response = session.post(url, data=info, cookies=cookie)
    time.sleep(1)
    standing_data = json.loads(response.text)["StandingsData"]

    # 各点数の順位範囲を求め、データを追加
    score_rank_dict: dict[int, list[int]] = {}
    for i in range(len(standing_data)):
        rank = standing_data[i]["Rank"]
        score = standing_data[i]["TotalResult"]["Score"] // 100
        if score in score_rank_dict:
            score_rank_dict[score][0] = min(score_rank_dict[score][0], rank)
            score_rank_dict[score][1] = max(score_rank_dict[score][1], rank)
        else:
            score_rank_dict[score] = [rank, rank]

    assert contest_name not in score_rank_data
    score_rank_data[contest_name] = score_rank_dict

# 追記
with open("data/points/points.txt", "w") as f:
    print("update points.txt")
    f.write(str(score_rank_data))
