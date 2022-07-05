# 早解き度とレートの相関を調べるために、19x5, 20x5年生まれの30回以上のアクティブ参加者の(ユーザー名, 補正後rating, rated参加数)の一覧を得る。

import urllib.request
import time

user_head = '<a href="/users/'
rate_head = "<td><b>"
times_head = "<td>"


Data = []
got = False  # これがFalseのまま＝そのページにユーザーはいないので、打ち切って次の年を調べる

for year in range(1905, 2025, 10):
    for page_no in range(1, 100):
        URL = "https://atcoder.jp/ranking?f.Affiliation=&f.BirthYearLowerBound={0}&f.BirthYearUpperBound={0}&f.CompetitionsLowerBound=30&f.CompetitionsUpperBound=9999&f.Country=&f.HighestRatingLowerBound=0&f.HighestRatingUpperBound=9999&f.RatingLowerBound=0&f.RatingUpperBound=9999&f.UserScreenName=&f.WinsLowerBound=0&f.WinsUpperBound=9999&page={1}".format(year, page_no)
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
                
                line = html[i+3]
                rate = ""
                ind = line.index(rate_head) + len(rate_head)
                while line[ind] != "<":
                    rate += line[ind]
                    ind += 1
                rate = int(rate)

                line = html[i+5]
                times = ""
                ind = line.index(times_head) + len(times_head)
                while line[ind] != "<":
                    times += line[ind]
                    ind += 1
                times = int(times)

                print(user_name, rate, times)
                Data.append([user_name, rate, times])
            
        if not got:
            break

f = open("analysis_1995/users_19x5.txt", "w")
for i in range(len(Data)):
    f.write("{} {} {}".format(Data[i][0], Data[i][1], Data[i][2]))
    f.write('\n')
f.close()