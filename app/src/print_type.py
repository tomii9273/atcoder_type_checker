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
        f = open("data/points/points.txt", "r")
        for item in f.readlines():
            main_D = ast.literal_eval(item)
            break
        f.close()
        self.main_D = main_D

    def get_rank_rate(self, user_name: str) -> tuple[float, float, int, int, int]:
        """AtCoder ID から平均順位率 (その得点を獲得した人数で重みづけしたもの・していないものの両方) を取得。補正値算出用。"""
        url = "https://atcoder.jp/users/{}/history/json".format(user_name)

        with urllib.request.urlopen(url) as res:
            html = res.read().decode("utf-8")
        js = json.loads(html)

        sum_per = 0
        per_w = 0
        sum_w = 0
        n_contest_for_calc = 0
        n_contest_rated = 0
        for i in range(len(js)):
            rated = js[i]["IsRated"]
            contest_name = js[i]["ContestScreenName"][:6]
            rank = js[i]["Place"]

            if rated:
                n_contest_rated += 1
            if rated and contest_name in self.main_D:
                V = list(self.main_D[contest_name].values())
                K = list(self.main_D[contest_name].keys())
                ind = 0
                while ind < len(V) and (not (V[ind][0] <= rank <= V[ind][1])):
                    ind += 1
                score = K[ind] if ind < len(K) else 0
                if score != 0 and V[ind][1] != V[ind][0]:
                    n_contest_for_calc += 1
                    per = (rank - V[ind][0]) / (V[ind][1] - V[ind][0])
                    weight = V[ind][1] - V[ind][0] + 1  # その得点を獲得した人数で重みづけする
                    per_w += per * weight
                    sum_w += weight
                    sum_per += per

        if n_contest_rated == 0:
            return (-1, -1, 0, 0, -1)
        rate4 = js[-1]["NewRating"]
        if n_contest_for_calc == 0:
            return (-1, -1, n_contest_for_calc, n_contest_rated, rate4)
        mean_rank_rate = sum_per / n_contest_for_calc
        weighted_mean_rank_rate = per_w / sum_w
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

        rate2 = rate_3_to_2(rate_4_to_3(int(rate4)), n_contest_rated)

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
