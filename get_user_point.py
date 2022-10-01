import datetime
import time
import urllib.request
from typing import Dict

from utils import slice_line


def get_user_point(
    contest_name: str, contest_start_time: datetime.datetime, contest_end_time: datetime.datetime, user_name: str
) -> int:
    """
    ある人の特定コンテスト中に獲得した得点を得る

    Args:
        contest_name (str): コンテスト名6文字 (axc000 の形式)
        contest_start_time (datetime.datetime): コンテスト開始時刻 (日本時間)
        contest_end_time (datetime.datetime): コンテスト終了時刻 (日本時間)
        user_name: ユーザー名 (AtCoder ID)

    Returns:
        int: コンテスト中に獲得した得点の合計値
    """
    assert len(contest_name) == 6

    submit_time_prefix = '<td class="no-break">' + "<time class='fixtime fixtime-second'>"  # クォーテーションの関係で分けて書いている
    submit_time_suffix = "+0900</time></td>"
    problem_name_prefix = '<td><a href="/contests/'
    problem_name_suffix = "</a></td>"
    score_prefix = ">"
    score_suffix = "</td>"

    problem_max_score: Dict[str, int] = {}  # 各問題の獲得得点

    for page_no in range(1, 10000):
        url = f"https://atcoder.jp/contests/{contest_name}/submissions?f.User={user_name}&page={page_no}"

        with urllib.request.urlopen(url) as res:
            html = res.read().decode("utf-8")
        time.sleep(1)
        html = list(html.split("\n"))

        line_ind = 0
        while line_ind < len(html):
            line = html[line_ind]
            break_flag = True
            if submit_time_prefix in line:
                break_flag = False
                submit_time = datetime.datetime.strptime(
                    slice_line(line, submit_time_prefix, submit_time_suffix), "%Y-%m-%d %H:%M:%S"
                )
                if contest_start_time <= submit_time < contest_end_time:  # (表記上)終了時刻と同時はコンテスト後扱いのはず
                    line_ind += 1
                    line = html[line_ind]
                    problem_name = slice_line(line, problem_name_prefix, problem_name_suffix)
                    line_ind += 3
                    line = html[line_ind]
                    score = int(slice_line(line, score_prefix, score_suffix))
                    if problem_name in problem_max_score:
                        # 単純に最高得点の提出をその問題の獲得得点と見なしているため、特殊な部分点の場合はうまくいかないかも
                        # 例: 互いに共通部分のない 3 制約 A, B, C があり、各制約に 100 点、合計 300 点の問題の場合
                        # 2 回提出し「提出1: A, B のみ正解 200 点」「提出2: A, C のみ正解 200 点」の場合、本当は 300 点とれているのに 200 点扱いになる
                        # (AtCoder の順位表でこれが 300 点と 200 点のどちらになるかは不明)
                        problem_max_score[problem_name] = max(problem_max_score[problem_name], score)
                    else:
                        problem_max_score[problem_name] = score
            line_ind += 1

        if break_flag:
            break

    if len(problem_max_score) == 0:
        score_sum = 0
    else:
        score_sum = sum(problem_max_score.values())

    return score_sum
