import argparse

from src.get_some_usernames import get_users_for_hosei
from src.output_result_5n_and_top import get_type_for_hosei


def make_new_hoseichi(file_name: str, debug: bool) -> None:
    """
    新しい補正値データを作成し、{file_name}.npy として保存する。
    debug = True のときは少人数で行う。
    """
    data = get_users_for_hosei(debug)
    get_type_for_hosei(data, file_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", type=str, required=True, help="新たに作成する補正値ファイルの名前")
    parser.add_argument("-d", "--debug", action="store_true", help="デバッグ実行か (補正値が 100 データのみになる)")
    args = parser.parse_args()

    make_new_hoseichi(file_name=args.name, debug=args.debug)
