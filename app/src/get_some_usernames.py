import time
import urllib.request

from bs4 import BeautifulSoup
from bs4.element import Tag


def get_one_user_data(block: Tag) -> tuple[str, int, int]:
    """1 ユーザーデータのブロックから (ユーザー名, レート, 参加回数) を取得する"""
    user_name = block.find_all("a", href=True)[1].find(["href", "span"]).get_text(strip=True)
    tds = block.find_all("td")
    rate4 = tds[3].get_text(strip=True)
    times = tds[5].get_text(strip=True)
    return user_name, int(rate4), int(times)


def parse_html_and_update_data(
    url: str, checked_users: set[str], data: list[tuple[str, int, int]]
) -> tuple[set[str], list[tuple[str, int, int]], int]:
    """
    1 ページの html データから、全ユーザーの (ユーザー名, レート, 参加回数) を取得し data に追加して、追加件数とともに返す
    checked_users: 取得済のユーザー名の集合 (重複防止のため)
    """
    with urllib.request.urlopen(url) as res:
        html_data = res.read().decode("utf-8")

    soup = BeautifulSoup(html_data, "html.parser")

    body_data = (
        soup.find("div", {"class": "table-responsive"})
        .find("table", {"class": "table table-bordered table-striped th-center"})
        .find("tbody")
    )
    user_blocks = body_data.find_all("tr")
    add_count = 0
    for block in user_blocks:
        user_name, rate4, times = get_one_user_data(block)
        if user_name not in checked_users:
            data.append((user_name, rate4, times))
            add_count += 1
            checked_users.add(user_name)
    return checked_users, data, add_count


def get_users_for_hosei(debug: bool = False) -> list[tuple[str, int, int]]:
    """
    早解き度とレートの相関を調べるために「(5 の倍数の西暦年生まれ or 補正後 rating が 2400 (橙色) 以上) かつ参加回数 30 回以上のアクティブユーザー」の
    (ユーザー名, 補正後 rating, rated 参加数) の一覧を得る。
    (debug = True のときは「1995 年生まれの参加回数 30 回以上のアクティブユーザーのうち、Rating 上位 100 人」のみ)
    """

    checked_users: set[str] = set()  # 取得済のユーザー名の集合 (重複防止のため)
    data: list[tuple[str, int, int]] = []  # (ユーザー名, レート, 参加回数) リスト

    print("get_users_for_hosei start")
    print("19x5-20x5 year start")

    # 5 の倍数の西暦年生まれのユーザーを集計
    years = list(range(1905, 2025, 5)) if not debug else [1995]
    for year in years:
        for page_no in range(1, 1000):
            url = (
                f"https://atcoder.jp/ranking?"
                f"f.Affiliation=&f.BirthYearLowerBound={year}&f.BirthYearUpperBound={year}&"
                f"f.CompetitionsLowerBound=30&f.CompetitionsUpperBound=9999&f.Country=&"
                f"f.HighestRatingLowerBound=0&f.HighestRatingUpperBound=9999&"
                f"f.RatingLowerBound=0&f.RatingUpperBound=9999&"
                f"f.UserScreenName=&f.WinsLowerBound=0&f.WinsUpperBound=9999&page={page_no}"
            )
            checked_users, data, add_count = parse_html_and_update_data(url, checked_users, data)
            time.sleep(1)
            if debug:
                print("debug end")
                return data
            if add_count == 0:  # 全ページを見終えた
                break

    print("19x5-20x5 year end")
    print("2400- rating start")

    # 補正後 rating が 2400 (橙色) 以上のユーザーを集計 (既に上記で集計したユーザーは除外)
    for page_no in range(1, 1000):
        url = (
            f"https://atcoder.jp/ranking?"
            f"contestType=algo&f.Affiliation=&"
            f"f.BirthYearLowerBound=0&f.BirthYearUpperBound=9999&"
            f"f.CompetitionsLowerBound=30&f.CompetitionsUpperBound=9999&f.Country=&"
            f"f.HighestRatingLowerBound=0&f.HighestRatingUpperBound=9999&"
            f"f.RatingLowerBound=2400&f.RatingUpperBound=9999&"
            f"f.UserScreenName=&f.WinsLowerBound=0&f.WinsUpperBound=9999&page={page_no}"
        )

        checked_users, data, add_count = parse_html_and_update_data(url, checked_users, data)
        time.sleep(1)
        if add_count == 0:  # 全ページを見終えた
            break

    print("2400- rating end")
    return data
