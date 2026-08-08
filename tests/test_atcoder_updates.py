import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import requests

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "app"))

from get_standing_and_join import standing_data_to_score_rank_dict  # noqa: E402
from src.atcoder_client import (  # noqa: E402
    AtCoderClient,
    AtCoderSessionError,
    filter_atcoder_cookies,
    get_atcoder_cookie_browsers,
)


class AtCoderClientTest(unittest.TestCase):
    def test_atcoder_cookieだけを抽出する(self) -> None:
        cookies = requests.cookies.RequestsCookieJar()
        cookies.set_cookie(
            requests.cookies.create_cookie(
                name="REVEL_SESSION",
                value="session",
                domain=".atcoder.jp",
            )
        )
        cookies.set_cookie(
            requests.cookies.create_cookie(
                name="subdomain",
                value="session",
                domain="sub.atcoder.jp",
            )
        )
        cookies.set_cookie(
            requests.cookies.create_cookie(
                name="unrelated",
                value="session",
                domain="notatcoder.jp",
            )
        )

        filtered_cookies = filter_atcoder_cookies(cookies)

        self.assertEqual(
            {cookie.name for cookie in filtered_cookies},
            {"REVEL_SESSION", "subdomain"},
        )

    def test_ブラウザの優先順を環境変数から取得する(self) -> None:
        with patch.dict(
            os.environ,
            {"ATCODER_COOKIE_BROWSER": " edge,Firefox, chrome "},
        ):
            self.assertEqual(
                get_atcoder_cookie_browsers(),
                ("edge", "firefox", "chrome"),
            )

    def test_ログイン画面への転送を検出する(self) -> None:
        response = requests.Response()
        response.status_code = 200
        response.url = "https://atcoder.jp/login?continue=%2Fsettings"

        client = AtCoderClient(sleep_sec=0)
        with patch.object(client.session, "get", return_value=response):
            with self.assertRaises(AtCoderSessionError):
                client.get_response(
                    "https://atcoder.jp/settings",
                    require_login=True,
                )
        client.close()


class StandingDataTest(unittest.TestCase):
    def test_同点者の順位範囲を作る(self) -> None:
        standing_data = [
            {"Rank": 1, "TotalResult": {"Score": 50000}},
            {"Rank": 2, "TotalResult": {"Score": 40000}},
            {"Rank": 3, "TotalResult": {"Score": 40000}},
            {"Rank": 4, "TotalResult": {"Score": 30000}},
        ]

        self.assertEqual(
            standing_data_to_score_rank_dict(standing_data),
            {
                500: [1, 1],
                400: [2, 3],
                300: [4, 4],
            },
        )


if __name__ == "__main__":
    unittest.main()
