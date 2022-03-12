from flask import Flask, render_template, request
from print_type_hoseitoru import get_type

app = Flask(__name__)

# getのときの処理
@app.route('/', methods=['GET'])
def get():
	return render_template('index.html', \
		message1 = 'AtCoder ID を入力してください。')

# postのときの処理	
@app.route('/', methods=['POST'])
def post():
    name = request.form['name']
    score, rate2, cnt, times, first_score, mean_score = get_type(name)
    mes1 = ""
    mes2 = ""
    mes3 = ""
    mes4 = ""
    if times == 0:
        mes = '{} さんは Rated なコンテストに参加していないか、または ID が存在しません。'.format(name)
    else:
        score *= 100
        mes = '{} さんのスコアは {:.2f} です。'.format(name, score)
        if -1 < score < 1:
            mes += '中間的なタイプです。'
        else:
            if 1 < abs(score) < 5:
                mes += 'わずかに、'
            elif abs(score) > 10:
                mes += 'かなり、'

            if score > 0:
                mes += '多く解く'
            else:
                mes += '早く解く'

            mes += 'タイプです。'
        if not (300 <= rate2 <= 3000):
            mes1 += '※内部レートが300～3000の範囲外のため、結果の信頼度が低い可能性があります。'
        mes2 = '{}さんの平均順位率: {:.4f}'.format(name, first_score)
        mes3 = '内部レートによる補正: {:.4f}'.format(mean_score)
        mes4 = '計算に使用したコンテスト数: {:}'.format(cnt)
        
    return render_template('index.html', \
        message = mes, message1 = mes1, message2 = mes2, message3 = mes3, message4 = mes4)

if __name__ == '__main__':
	app.run()