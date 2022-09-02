# 早解き度とレートの相関を調べるために、(5の倍数の西暦年生まれ or 補正後rating2400(橙)以上) かつ30回以上のアクティブ参加者の(ユーザー名, 補正後rating, rated参加数)の一覧を得る。

import time
import urllib.request

user_head = '<a href="/users/'
rate_head = "<td><b>"
times_head = "<td>"


Data = []
got = False  # これがFalseのまま＝そのページにユーザーはいないので、打ち切って次の年を調べる
checked_users = set()

# 5の倍数の西暦年生まれのユーザーを集計
for year in range(1905, 2025, 5):
    for page_no in range(1, 1000):
        URL = "https://atcoder.jp/ranking?f.Affiliation=&f.BirthYearLowerBound={0}&f.BirthYearUpperBound={0}&f.CompetitionsLowerBound=30&f.CompetitionsUpperBound=9999&f.Country=&f.HighestRatingLowerBound=0&f.HighestRatingUpperBound=9999&f.RatingLowerBound=0&f.RatingUpperBound=9999&f.UserScreenName=&f.WinsLowerBound=0&f.WinsUpperBound=9999&page={1}".format(
            year, page_no
        )
        with urllib.request.urlopen(URL) as res:
            html = res.read().decode("utf-8")
        # print(html)
        time.sleep(1)
        html = list(html.split("\n"))
        # print(len(html))
        got = False
        for i in range(len(html)):
            line = html[i]
            if user_head in line:
                got = True
                user_name = ""
                ind = line.index(user_head) + len(user_head)
                while line[ind] != '"':
                    user_name += line[ind]
                    ind += 1

                line = html[i + 3]
                rate = ""
                ind = line.index(rate_head) + len(rate_head)
                while line[ind] != "<":
                    rate += line[ind]
                    ind += 1
                rate = int(rate)

                line = html[i + 5]
                times = ""
                ind = line.index(times_head) + len(times_head)
                while line[ind] != "<":
                    times += line[ind]
                    ind += 1
                times = int(times)

                print(user_name, rate, times)
                Data.append([user_name, rate, times])
                checked_users.add(user_name)

        if not got:
            break


# 補正後rating2400(橙)以上のユーザーを集計 (既に上記で集計したユーザーは除外)
for page_no in range(1, 1000):
    URL = f"https://atcoder.jp/ranking?contestType=algo&f.Affiliation=&f.BirthYearLowerBound=0&f.BirthYearUpperBound=9999&f.CompetitionsLowerBound=30&f.CompetitionsUpperBound=9999&f.Country=&f.HighestRatingLowerBound=0&f.HighestRatingUpperBound=9999&f.RatingLowerBound=2400&f.RatingUpperBound=9999&f.UserScreenName=&f.WinsLowerBound=0&f.WinsUpperBound=9999&page={page_no}"
    with urllib.request.urlopen(URL) as res:
        html = res.read().decode("utf-8")
    # print(html)
    time.sleep(1)
    html = list(html.split("\n"))
    # print(len(html))
    got = False
    for i in range(len(html)):
        line = html[i]
        if user_head in line:
            got = True
            user_name = ""
            ind = line.index(user_head) + len(user_head)
            while line[ind] != '"':
                user_name += line[ind]
                ind += 1

            line = html[i + 3]
            rate = ""
            ind = line.index(rate_head) + len(rate_head)
            while line[ind] != "<":
                rate += line[ind]
                ind += 1
            rate = int(rate)

            line = html[i + 5]
            times = ""
            ind = line.index(times_head) + len(times_head)
            while line[ind] != "<":
                times += line[ind]
                ind += 1
            times = int(times)

            if user_name not in checked_users:
                print(user_name, rate, times)
                Data.append([user_name, rate, times])
                checked_users.add(user_name)

    if not got:
        break


f = open("ignore/analysis_1995/users_5n_and_top_20220829.txt", "w")
for i in range(len(Data)):
    f.write("{} {} {}".format(Data[i][0], Data[i][1], Data[i][2]))
    f.write("\n")
f.close()
