# 最小二乗法で求める補正値ラインの次数 (2 だとトップ層でアンダーフィットだったので 10 に変更)
DEGREE_OF_HOSEI_CURVE = 10

# 算出に使う補正値 (の式の作成に用いる (内部レート, 平均順位率) 一覧) のファイルのパス
HOSEICHI_FILE_PATH = "data/hoseichi/hoseichi_5ntop_20230829.npy"

# 重みづけした平均順位率・スコアを取得するか
USE_WEIGHTED_MEAN_RANK_RATE = True
