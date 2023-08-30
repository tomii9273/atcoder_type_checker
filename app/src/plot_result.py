from io import StringIO

import japanize_matplotlib  # noqa
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from .const import DEGREE_OF_HOSEI_CURVE, HOSEICHI_FILE_PATH

matplotlib.use("Agg")


def plot_result(name: str, rate2: float, first_score: float, times: int, weighted: bool) -> str:
    """
    補正値などとともに、1 ユーザーの結果をプロットした図 (を表す文字列) を返す。
    集計対象のコンテスト回数 0 の場合は、ユーザーの結果以外をプロットしたものを返す。
    weighted: 重みづけした補正値 (としての平均順位率) を使用するか。
    """

    N = np.load(HOSEICHI_FILE_PATH).T

    x = N[0]
    if weighted:
        y = N[2]
    else:
        y = N[1]

    fig = plt.figure(figsize=(10, 5))

    p2 = np.poly1d(np.polyfit(x, y, DEGREE_OF_HOSEI_CURVE))

    xp = np.linspace(-500, 4000, 100)

    if times > 0:
        plt.scatter([rate2], [first_score], marker="o", color="red", s=50, zorder=3, label=f"{name} さんの位置")

    plt.plot(xp, p2(xp), "-", color="k", label="内部レートによる補正値 (スコア 0 ライン)", zorder=2)
    plt.plot(xp, p2(xp) + 0.1, "--", color="k", label="スコア ±10 ライン", zorder=2)
    plt.plot(x, y, ".", color="#1f77b4", label=f"補正値算出に使用したユーザー ({len(x)} 人)", zorder=1)
    plt.plot(xp, p2(xp) - 0.1, "--", color="k", zorder=1)

    cols = [
        "#808080",
        "#804000",
        "#008000",
        "#00C0C0",
        "#0000FF",
        "#C0C000",
        "#FF8000",
        "#FF0000",
    ]

    rate_min = min(min(x), rate2) - 50
    rate_max = max(4000, max(max(x), rate2) + 50)

    rates = [rate_min] + [i for i in range(400, 2801, 400)] + [rate_max]

    for i, col in enumerate(cols):
        plt.axvspan(rates[i], rates[i + 1], alpha=0.3, color=col, zorder=0)

    plt.ylim(0, 1)
    plt.xlim(rate_min, rate_max)
    plt.xlabel("内部レート")
    plt.ylabel("平均順位率")
    plt.grid(axis="y")
    plt.rcParams["axes.axisbelow"] = True
    plt.legend()

    # StringIOを用いて画像を文字列として保存

    strio = StringIO()
    fig.savefig(strio, format="svg")
    plt.close(fig)

    strio.seek(0)
    contents = strio.getvalue()
    svgstr = contents[contents.index("<svg") :]

    return svgstr
