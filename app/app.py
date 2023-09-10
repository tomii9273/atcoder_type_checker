#!/usr/bin/env python3

import re

from flask import Flask, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from src.const import HOSEICHI_FILE_PATH, USE_WEIGHTED_MEAN_RANK_RATE
from src.plot_result import plot_result
from src.print_type import Calc
from src.utils import add_b, add_p, load_txt_one_line

app = Flask(__name__)
app.config["RATELIMIT_HEADERS_ENABLED"] = True  # ヘッダーに RateLimit 情報を出力
limiter = Limiter(get_remote_address, app=app, default_limits=["50 per minute"])


DATE_SITE = load_txt_one_line("data/update_dates/date_site.txt")
DATE_RANK_DATA = load_txt_one_line("data/update_dates/date_rank_data.txt")
DATE_HOSEICHI = load_txt_one_line("data/update_dates/date_hoseichi.txt")


# get のときの処理
@app.route("/", methods=["GET"])
def get():
    mes_get = "AtCoder ID を入力してください。"
    return render_template(
        "index.html",
        message=add_p(add_b(mes_get)),
        date_site=DATE_SITE,
        date_rank_data=DATE_RANK_DATA,
        date_hoseichi=DATE_HOSEICHI,
    )


# post のときの処理
@app.route("/", methods=["POST"])
def post():
    raw_name = request.form["name"]
    name = "".join(re.findall("[a-zA-Z0-9_]+", raw_name))
    calc = Calc()
    hosei_mean_rank_rate, rate2, n_contest_for_calc, mean_rank_rate, hoseichi = calc.get_score(
        user_name=name, hoseichi_file_path=HOSEICHI_FILE_PATH, weighted=USE_WEIGHTED_MEAN_RANK_RATE
    )
    if n_contest_for_calc == 0:
        mes_main = "{} さんは集計対象となるような参加の回数が 0 回であるか、または ID が存在しません。".format(name)
        mes_for_tweet = mes_main
        mes = add_p(add_b(mes_main))
    else:
        score = 100 * hosei_mean_rank_rate
        mes_main = "{} さんのスコアは {:.2f} です。".format(name, score)
        mes_outlier = ""
        if score < -10:
            mes_main += "かなり、早く解くタイプです。"
        elif score < -5:
            mes_main += "早く解くタイプです。"
        elif score < -1:
            mes_main += "わずかに、早く解くタイプです。"
        elif score < 1:
            mes_main += "中間的なタイプです。"
        elif score < 5:
            mes_main += "わずかに、多く解くタイプです。"
        elif score < 10:
            mes_main += "多く解くタイプです。"
        else:
            mes_main += "かなり、多く解くタイプです。"

        if not (0 <= rate2 <= 3200):
            mes_outlier += "※ 内部レートが 0 ～ 3200 の範囲外のため、サンプル不足により結果の信頼度が低くなっています。"

        mes_inner_rate = "{} さんの内部レート: {:.2f}".format(name, rate2)
        mes_n_contest = "計算に使用したコンテスト数: {:}".format(n_contest_for_calc)
        mes_mean_rank_rate = "{} さんの平均順位率: {:.4f}".format(name, mean_rank_rate)
        mes_hosei = "内部レートによる補正値: {:.4f} ({} さんと同程度の内部レートの人が平均的に取得している平均順位率)".format(hoseichi, name)
        mes_score = "スコアは下図の黒実線と赤丸の y 座標の差を 100 倍し、符号を付けたものです。"

        mes = (
            add_p(add_b(mes_main))
            + add_p(add_b(mes_outlier))
            + add_p(mes_inner_rate)
            + add_p(mes_n_contest)
            + add_p(mes_mean_rank_rate)
            + add_p(mes_hosei)
            + add_p(add_b(mes_score))
        )

        mes_for_tweet = mes_main
        if mes_outlier != "":
            mes_for_tweet += " (" + mes_outlier + ")"
        mes_for_tweet += " (" + mes_n_contest + ")"

    return render_template(
        "index.html",
        message=mes,
        message_for_tweet=mes_for_tweet,
        svgstr=plot_result(
            name=name,
            rate2=rate2,
            mean_rank_rate=mean_rank_rate,
            n_contest=n_contest_for_calc,
            weighted=USE_WEIGHTED_MEAN_RANK_RATE,
        ),
        date_site=DATE_SITE,
        date_rank_data=DATE_RANK_DATA,
        date_hoseichi=DATE_HOSEICHI,
    )


# 以下、サブページの表示
@app.route("/qa", methods=["GET"])
def qa():
    return render_template("qa.html")


if __name__ == "__main__":
    app.run(debug=True)
