import re

from flask import Flask, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from plot_result import plot_result
from print_type_hoseitoru import get_type
from utils import load_txt_one_line

app = Flask(__name__)
app.config["RATELIMIT_HEADERS_ENABLED"] = True  # ヘッダーに RateLimit 情報を出力
limiter = Limiter(get_remote_address, app=app, default_limits=["50 per minute"])


def add_p(s: str) -> str:
    return "<p>" + s + "</p>"


def add_b(s: str) -> str:
    return "<b>" + s + "</b>"


# getのときの処理
@app.route("/", methods=["GET"])
def get():
    return render_template(
        "index.html",
        message1="AtCoder ID を入力してください。",
        date_site=load_txt_one_line("update_dates/date_site.txt"),
        date_rank_data=load_txt_one_line("update_dates/date_rank_data.txt"),
    )


# postのときの処理
@app.route("/", methods=["POST"])
def post():
    raw_name = request.form["name"]
    name = "".join(re.findall("[a-zA-Z0-9_]+", raw_name))
    score, rate2, times, first_score, mean_score = get_type(name)
    if times == 0:
        mes_main = "{} さんは集計対象となるような参加の回数が 0 回であるか、または ID が存在しません。".format(name)
        mes_for_tweet = mes_main
        mes = add_p(add_b(mes_main))
    else:
        score *= 100
        mes_main = "{} さんのスコアは {:.2f} です。".format(name, score)
        mes_outlier = ""
        if -1 < score < 1:
            mes_main += "中間的なタイプです。"
        else:
            if 1 < abs(score) < 5:
                mes_main += "わずかに、"
            elif abs(score) > 10:
                mes_main += "かなり、"

            if score > 0:
                mes_main += "多く解く"
            else:
                mes_main += "早く解く"

            mes_main += "タイプです。"
        if not (0 <= rate2 <= 3200):
            mes_outlier += "※ 内部レートが 0 ～ 3200 の範囲外のため、結果の信頼度が低い可能性があります。"

        mes_inner_rate = "{} さんの内部レート: {:.2f}".format(name, rate2)
        mes_n_contest = "計算に使用したコンテスト数: {:}".format(times)
        mes_mean_rank_rate = "{} さんの平均順位率: {:.4f}".format(name, first_score)
        mes_hosei = "内部レートによる補正値: {:.4f} ({} さんと同程度の内部レートの人が取得している、平均的な平均順位率)".format(mean_score, name)
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
        svgstr=plot_result(name, rate2, first_score, times),
        date_site=load_txt_one_line("update_dates/date_site.txt"),
        date_rank_data=load_txt_one_line("update_dates/date_rank_data.txt"),
    )


# 以下、サブページの表示
@app.route("/qa", methods=["GET"])
def qa():
    return render_template("qa.html")


if __name__ == "__main__":
    app.run()
