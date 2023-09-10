import ast
import json
import urllib.request

import numpy as np

from .const import DEGREE_OF_HOSEI_CURVE
from .utils import rate_3_to_2, rate_4_to_3


class Calc:
    """平均順位率・スコア・補正値などの取得を行うクラス"""

    def __init__(self) -> None:
        """順位データを読み込む。"""
        with open("data/points/points.txt", "r") as f:
            first_line = f.readline().strip()
            self.score_rank_data = ast.literal_eval(first_line)

    def get_rank_rate(self, user_name: str) -> tuple[float, float, int, int, int]:
        """AtCoder ID から平均順位率 (その得点を獲得した人数で重みづけしたもの・していないものの両方) を取得。補正値算出用。"""
        url = f"https://atcoder.jp/users/{user_name}/history/json"

        with urllib.request.urlopen(url) as res:
            html = res.read().decode("utf-8")
        history = json.loads(html)

        sum_rank_rate = 0
        sum_weighted_rank_rate = 0
        sum_weight = 0
        n_contest_for_calc = 0
        n_contest_rated = 0

        for i in range(len(history)):
            rated = history[i]["IsRated"]
            contest_name = history[i]["ContestScreenName"][:6]
            rank = history[i]["Place"]

            if rated:
                n_contest_rated += 1
            if rated and contest_name in self.score_rank_data:
                scores = list(self.score_rank_data[contest_name].keys())
                rank_ranges = list(self.score_rank_data[contest_name].values())
                ind = 0
                while ind < len(scores) and (not (rank_ranges[ind][0] <= rank <= rank_ranges[ind][1])):
                    ind += 1
                # 主に 0 点の場合、まれに (成績表の順位) > (順位表の 0 点の順位) となることがある。その場合のエラーを回避し 0 点として扱う。
                score = scores[ind] if ind < len(scores) else 0
                rank_l, rank_r = rank_ranges[ind][0], rank_ranges[ind][1]
                if score != 0 and rank_l != rank_r:
                    n_contest_for_calc += 1
                    rank_rate = (rank - rank_l) / (rank_r - rank_l)
                    weight = rank_r - rank_l + 1  # その得点を獲得した人数で重みづけする
                    sum_rank_rate += rank_rate
                    sum_weighted_rank_rate += rank_rate * weight
                    sum_weight += weight

        if n_contest_rated == 0:
            return (-1, -1, 0, 0, -1)

        rate4 = history[-1]["NewRating"]

        if n_contest_for_calc == 0:
            return (-1, -1, n_contest_for_calc, n_contest_rated, rate4)

        mean_rank_rate = sum_rank_rate / n_contest_for_calc
        weighted_mean_rank_rate = sum_weighted_rank_rate / sum_weight
        return (mean_rank_rate, weighted_mean_rank_rate, n_contest_for_calc, n_contest_rated, rate4)

    def get_score(
        self, user_name: str, hoseichi_file_path: str, weighted: bool
    ) -> tuple[float, float, int, float, float]:
        """
        AtCoder ID と補正値ファイルから、平均順位率とスコア (の元となる補正済み平均順位率) を取得。
        weighted: 重みづけした平均順位率・スコアを取得するか。
        """

        mean_rank_rate, weighted_mean_rank_rate, n_contest_for_calc, n_contest_rated, rate4 = self.get_rank_rate(
            user_name
        )

        if n_contest_rated == 0:
            return (-1, -1, 0, -1, -1)

        rate2 = rate_3_to_2(rate_4_to_3(rate4), n_contest_rated)

        if n_contest_for_calc == 0:
            return (-1, -1, n_contest_for_calc, n_contest_rated, rate4)

        N = np.load(hoseichi_file_path).T

        if weighted:
            get_weighted_hoseichi = np.poly1d(np.polyfit(N[0], N[2], DEGREE_OF_HOSEI_CURVE))
            weighted_hoseichi = get_weighted_hoseichi(rate2)
            weighted_hosei_mean_rank_rate = weighted_mean_rank_rate - weighted_hoseichi
            return (
                weighted_hosei_mean_rank_rate,
                rate2,
                n_contest_for_calc,
                weighted_mean_rank_rate,
                weighted_hoseichi,
            )
        else:
            get_hoseichi = np.poly1d(np.polyfit(N[0], N[1], DEGREE_OF_HOSEI_CURVE))
            hoseichi = get_hoseichi(rate2)
            hosei_mean_rank_rate = mean_rank_rate - hoseichi
            return (hosei_mean_rank_rate, rate2, n_contest_for_calc, mean_rank_rate, hoseichi)
