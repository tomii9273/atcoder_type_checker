import ast
import json
import urllib.request
from typing import Any

import numpy as np

from .atcoder_client import AtCoderClient
from .const import DEGREE_OF_HOSEI_CURVE
from .utils import rate_3_to_2, rate_4_to_3


class Calc:
    """平均順位率やスコア、補正値などの計算を行うクラス。"""

    def __init__(self, client: AtCoderClient | None = None) -> None:
        """score -> rank 範囲のデータを読み込む。"""
        with open("data/points/points.txt", "r", encoding="utf-8") as f:
            first_line = f.readline().strip()
            self.score_rank_data = ast.literal_eval(first_line)
        self.client = client

    def get_history(self, user_name: str) -> list[dict[str, Any]]:
        """ユーザーの成績履歴 JSON を取得する。"""
        url = f"https://atcoder.jp/users/{user_name}/history/json"

        if self.client is None:
            with urllib.request.urlopen(url) as res:
                raw_text = res.read().decode("utf-8")
            return json.loads(raw_text)

        return self.client.get_json(url)

    def get_rank_rate(self, user_name: str) -> tuple[float, float, int, int, int]:
        """AtCoder ID から平均順位率などを計算して返す。"""
        history = self.get_history(user_name)

        sum_rank_rate = 0
        sum_weighted_rank_rate = 0
        sum_weight = 0
        n_contest_for_calc = 0
        n_contest_rated = 0

        for one_history in history:
            rated = one_history["IsRated"]
            contest_name = one_history["ContestScreenName"][:6]
            rank = one_history["Place"]

            if rated:
                n_contest_rated += 1

            if rated and contest_name in self.score_rank_data:
                scores = list(self.score_rank_data[contest_name].keys())
                rank_ranges = list(self.score_rank_data[contest_name].values())
                ind = 0
                while ind < len(scores) and not (rank_ranges[ind][0] <= rank <= rank_ranges[ind][1]):
                    ind += 1

                score = scores[ind] if ind < len(scores) else 0
                if score == 0:
                    continue
                rank_l, rank_r = rank_ranges[ind][0], rank_ranges[ind][1]
                if rank_l == rank_r:
                    continue
                n_contest_for_calc += 1
                rank_rate = (rank - rank_l) / (rank_r - rank_l)
                weight = rank_r - rank_l + 1
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
        return (
            mean_rank_rate,
            weighted_mean_rank_rate,
            n_contest_for_calc,
            n_contest_rated,
            rate4,
        )

    def get_score(
        self, user_name: str, hoseichi_file_path: str, weighted: bool
    ) -> tuple[float, float, int, float, float]:
        """
        AtCoder ID と補正値ファイルから、
        補正込み平均順位率と関連値を返す。
        """
        (
            mean_rank_rate,
            weighted_mean_rank_rate,
            n_contest_for_calc,
            n_contest_rated,
            rate4,
        ) = self.get_rank_rate(user_name)

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

        get_hoseichi = np.poly1d(np.polyfit(N[0], N[1], DEGREE_OF_HOSEI_CURVE))
        hoseichi = get_hoseichi(rate2)
        hosei_mean_rank_rate = mean_rank_rate - hoseichi
        return (hosei_mean_rank_rate, rate2, n_contest_for_calc, mean_rank_rate, hoseichi)
