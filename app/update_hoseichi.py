#!/usr/bin/env python3

import argparse

from src.atcoder_client import AtCoderClient
from src.get_some_usernames import get_users_for_hosei
from src.output_result_5n_and_top import get_type_for_hosei


def make_new_hoseichi(
    file_name: str,
    debug: bool,
    client: AtCoderClient | None = None,
) -> str:
    """
    新しい補正値データを生成して保存する。
    debug = True のときは少人数だけで実行する。
    """
    if client is None:
        with AtCoderClient(use_browser_cookie=True) as browser_client:
            browser_client.validate_login()
            return make_new_hoseichi(
                file_name=file_name,
                debug=debug,
                client=browser_client,
            )

    data = get_users_for_hosei(debug, client=client)
    assert debug or 1000 <= len(data) <= 5000, f"len(data) out of range: {len(data)}"
    return get_type_for_hosei(data, file_name, client=client)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-n",
        "--name",
        type=str,
        required=True,
        help="新たに保存する補正値ファイル名",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="デバッグ実行か (補正値は 100 データのみになる)",
    )
    args = parser.parse_args()

    print("通常ブラウザの AtCoder ログイン済み Cookie を使って補正値データを更新します。")
    make_new_hoseichi(file_name=args.name, debug=args.debug)
