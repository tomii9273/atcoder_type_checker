#!/usr/bin/env python3

import argparse
import ast
import re
from typing import Any

from bs4 import BeautifulSoup

from src.atcoder_client import AtCoderClient


def url_to_bs(url: str, client: AtCoderClient) -> BeautifulSoup:
    """ブラウザセッションを使って URL から BeautifulSoup を生成する。"""
    return client.get_bs(url)


def standing_data_to_score_rank_dict(
    standing_data: list[dict[str, Any]],
) -> dict[int, list[int]]:
    """standings/json の内容を score -> rank 範囲に変換する。"""
    score_rank_dict: dict[int, list[int]] = {}
    for one_standing_data in standing_data:
        rank = int(one_standing_data["Rank"])
        score = int(one_standing_data["TotalResult"]["Score"]) // 100
        if score in score_rank_dict:
            score_rank_dict[score][0] = min(score_rank_dict[score][0], rank)
            score_rank_dict[score][1] = max(score_rank_dict[score][1], rank)
        else:
            score_rank_dict[score] = [rank, rank]

    return score_rank_dict


def get_score_rank_dict(
    contest_name: str,
    client: AtCoderClient,
) -> dict[int, list[int]]:
    """1 コンテスト分の standings/json から score -> rank 範囲を作る。"""
    response_data = client.get_json(
        f"https://atcoder.jp/contests/{contest_name}/standings/json",
        require_login=True,
    )
    standing_data = response_data["StandingsData"]
    return standing_data_to_score_rank_dict(standing_data)


def get_contest_names(
    client: AtCoderClient,
    contest_names_exist: set[str],
    backfill: bool,
) -> set[str]:
    """アーカイブから未取得の ABC・ARC・AGC を探す。"""
    contest_names: set[str] = set()
    for page_no in range(1, 1000):
        archive_url = "https://atcoder.jp/contests/archive"
        if page_no >= 2:
            archive_url += f"?page={page_no}"
        bs = url_to_bs(archive_url, client=client)

        table_container = bs.find("div", {"class": "table-responsive"})
        if table_container is None:
            break
        table = table_container.find(
            "table",
            {"class": ("table table-default table-striped table-hover " "table-condensed table-bordered small")},
        )
        if table is None:
            break
        body_data = table.find("tbody")
        if body_data is None:
            break
        contest_blocks = body_data.find_all("tr")
        if len(contest_blocks) == 0:
            break

        contest_names_on_page = set()
        for block in contest_blocks:
            contest_name = block.find_all("td")[1].find("a", href=True)["href"].split("/")[-1]
            if re.fullmatch(r"a[brg]c[0-9]{3}", contest_name):
                contest_names_on_page.add(contest_name)

        new_contest_names = contest_names_on_page - contest_names_exist
        contest_names.update(new_contest_names)
        print(f"archive page {page_no}: " f"対象 {len(contest_names_on_page)} 件、未取得 {len(new_contest_names)} 件")

        if not backfill and len(contest_names_on_page) > 0 and contest_names_on_page <= contest_names_exist:
            break

    return contest_names


def get_standing_and_join(
    client: AtCoderClient | None = None,
    backfill: bool = False,
) -> None:
    """新しいコンテストの順位範囲データを points.txt に追加する。"""
    if client is None:
        with AtCoderClient(use_browser_cookie=True) as browser_client:
            browser_client.validate_login()
            get_standing_and_join(client=browser_client, backfill=backfill)
        return

    with open("data/points/points.txt", "r", encoding="utf-8") as f:
        first_line = f.readline().strip()
        score_rank_data = ast.literal_eval(first_line)
        contest_names_exist = set(score_rank_data.keys())

    contest_names = sorted(
        get_contest_names(
            client=client,
            contest_names_exist=contest_names_exist,
            backfill=backfill,
        )
    )
    print("新たに standings/json を取得するコンテストの一覧:", contest_names)

    if len(contest_names) == 0:
        return

    for contest_name in contest_names:
        print("start", contest_name)
        assert contest_name not in score_rank_data
        score_rank_data[contest_name] = get_score_rank_dict(contest_name, client=client)

    with open("data/points/points.txt", "w", encoding="utf-8") as f:
        print("update points.txt")
        f.write(str(score_rank_data))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--backfill",
        action="store_true",
        help="アーカイブ全ページを確認して過去の未取得コンテストも補完する。",
    )
    args = parser.parse_args()

    print("通常ブラウザの AtCoder ログイン済み Cookie を使って順位データを更新します。")
    get_standing_and_join(backfill=args.backfill)
