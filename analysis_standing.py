# 得た順位表jsonから、各点数の順位範囲を求め、一つのtxtファイルに保存する。

import codecs
import json

contest_names = ["abc{:03}".format(i) for i in range(195, 0, -1)] \
+ ["arc{:03}".format(i) for i in range(114, 0, -1)] \
+ ["agc{:03}".format(i) for i in range(52, 0, -1)]

main_D = {}

for contest_name in contest_names:
    print("load", contest_name)
    D = {}
    f = codecs.open("results/{}.txt".format(contest_name), "r", "utf-8")
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
    

f = open("points/points_{}_files.txt".format(len(main_D)), "w")
f.write(str(main_D))
f.close()