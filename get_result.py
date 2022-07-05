# 各コンテストのレーティング変化表（results）のjsonを取得する。順位表（standings）のjsonの取得と違い、ログイン（認証）する必要がない。
# 現状使用していない。

import codecs
import time
import urllib.request

contest_names = ["arc114", "abc193"]

for contest_name in contest_names:
    URL = "https://atcoder.jp/contests/{}/results/json".format(contest_name)
    with urllib.request.urlopen(URL) as res:
        html = res.read().decode("utf-8")
    # print(html)
    time.sleep(1)
    html = list(html.split("\n"))
    f = codecs.open("results/{}.txt".format(contest_name), "w", "utf-8")
    print(len(html))
    for i in range(len(html)):
        f.write(html[i])
    f.close()
