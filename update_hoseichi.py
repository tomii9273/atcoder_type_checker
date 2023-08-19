import sys

from get_some_usernames import get_users_for_hosei
from output_result_5n_and_top import get_type_for_hosei


def make_new_hoseichi(file_name: str) -> None:
    data = get_users_for_hosei()
    get_type_for_hosei(data, file_name)


if __name__ == "__main__":
    make_new_hoseichi(sys.argv[1])
