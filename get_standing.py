# 各コンテストの順位表jsonを取得する。ログイン（認証）する必要あり。

import codecs
import time

import requests
from bs4 import BeautifulSoup

# contest_names = ["agc{:03}".format(i) for i in range(52, 0, -1)]
contest_names = "abc196", "arc115"


pw = input("Password?: ")

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
    f = codecs.open("results/{}.txt".format(contest_name), "w", "utf-8")
    f.write(res.text)
    f.close()
