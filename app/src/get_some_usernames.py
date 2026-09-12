import urllib.request
from datetime import datetime

from bs4 import BeautifulSoup
from bs4.element import Tag

from .atcoder_client import AtCoderClient


def get_one_user_data(block: Tag) -> tuple[str, int, int]:
    """1 ユーザー分の (ユーザー名, レート, Rated 参加回数) を取得する。"""
    user_name = block.find_all("a", href=True)[1].find(["href", "span"]).get_text(strip=True)
    tds = block.find_all("td")
    rate4 = tds[3].get_text(strip=True)
    times = tds[5].get_text(strip=True)
    return user_name, int(rate4), int(times)


def parse_html_and_update_data(
    url: str,
    checked_users: set[str],
    data: list[tuple[str, int, int]],
    client: AtCoderClient | None = None,
) -> tuple[set[str], list[tuple[str, int, int]], int]:
    """
    1 ページ分の HTML から必要なユーザー情報を追加して、
    追加件数も返す。
    """
    if client is None:
        with urllib.request.urlopen(url) as res:
            html_data = res.read().decode("utf-8")
        soup = BeautifulSoup(html_data, "html.parser")
    else:
        soup = client.get_bs(url)

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


def get_users_for_hosei(debug: bool = False, client: AtCoderClient | None = None) -> list[tuple[str, int, int]]:
    """
    補正値作成に使うユーザー一覧を取得する。
    19x5 - 20x5 年生まれ、またはレート 2400 以上のうち、
    Rated 参加回数 30 回以上の Algo ユーザーを集める。
    """
    checked_users: set[str] = set()
    data: list[tuple[str, int, int]] = []

    print("get_users_for_hosei start")
    print("19x5-20x5 year start")

    years = list(range(1905, datetime.now().year + 1, 5)) if not debug else [1995]
    for year in years:
        for page_no in range(1, 1000):
            url = (
                "https://atcoder.jp/ranking?contestType=algo"
                f"&f.CompetitionsLowerBound=30&f.BirthYearLowerBound={year}"
                f"&f.BirthYearUpperBound={year}&page={page_no}"
            )
            checked_users, data, add_count = parse_html_and_update_data(url, checked_users, data, client=client)
            if debug:
                print("debug end")
                return data
            if add_count == 0:
                break
            print(f"got year {year} page_no {page_no}")

    print(f"19x5-20x5 year end (total {len(checked_users)} users)")
    print("2400- rating start")

    for page_no in range(1, 1000):
        url = (
            "https://atcoder.jp/ranking?contestType=algo"
            f"&f.CompetitionsLowerBound=30&f.RatingLowerBound=2400&page={page_no}"
        )
        checked_users, data, add_count = parse_html_and_update_data(url, checked_users, data, client=client)
        if add_count == 0:
            break
        print(f"got page_no {page_no}")

    print("2400- rating end")
    print(f"total {len(checked_users)} users")
    return data
