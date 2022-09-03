from flask import Flask, render_template, request

from plot_result import plot_result
from print_type_hoseitoru import get_type

app = Flask(__name__)

# getのときの処理
@app.route("/", methods=["GET"])
def get():
    return render_template("index.html", message1="AtCoder ID を入力してください。")


# postのときの処理
@app.route("/", methods=["POST"])
def post():
    name = request.form["name"]
    score, rate2, times, first_score, mean_score = get_type(name)
    mes1 = ""
    mes2 = ""
    mes3 = ""
    mes4 = ""
    mes5 = ""
    mes6 = ""
    if times == 0:
        mes = "{} さんは集計対象となるような参加の回数が 0 回であるか、または ID が存在しません。".format(name)
    else:
        score *= 100
        mes = "{} さんのスコアは {:.2f} です。".format(name, score)
        if -1 < score < 1:
            mes += "中間的なタイプです。"
        else:
            if 1 < abs(score) < 5:
                mes += "わずかに、"
            elif abs(score) > 10:
                mes += "かなり、"

            if score > 0:
                mes += "多く解く"
            else:
                mes += "早く解く"

            mes += "タイプです。"
        if not (0 <= rate2 <= 3200):
            mes1 += "※内部レートが 0 ～ 3200 の範囲外のため、結果の信頼度が低い可能性があります。"
        mes2 = "{} さんの内部レート: {:.2f}".format(name, rate2)
        mes3 = "計算に使用したコンテスト数: {:}".format(times)
        mes4 = "{} さんの平均順位率: {:.4f}".format(name, first_score)
        mes5 = "内部レートによる補正値: {:.4f} (= {} さんと同程度の内部レートの人が取得している、平均的な平均順位率)".format(mean_score, name)
        mes6 = "スコアは下図の黒実線と赤丸の y 座標の差を 100 倍し、符号を付けたものです。"

    return render_template(
        "index.html",
        message=mes,
        message1=mes1,
        message2=mes2,
        message3=mes3,
        message4=mes4,
        message5=mes5,
        message6=mes6,
        svgstr=plot_result(name, rate2, first_score, times),
    )


if __name__ == "__main__":
    app.run()
