from io import StringIO

import japanize_matplotlib  # noqa
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from .const import DEGREE_OF_HOSEI_CURVE, HOSEICHI_FILE_PATH

matplotlib.use("Agg")


def plot_result(name: str, rate2: float, mean_rank_rate: float, n_contest: int, weighted: bool) -> str:
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

    fig, ax = plt.subplots(figsize=(10, 5))

    get_hoseichi = np.poly1d(np.polyfit(x, y, DEGREE_OF_HOSEI_CURVE))

    x_line = np.linspace(-500, 4000, 100)

    if n_contest > 0:
        ax.scatter([rate2], [mean_rank_rate], marker="o", color="red", s=50, zorder=3, label=f"{name} さんの位置")

    ax.set_axisbelow(True)
    ax.plot(x_line, get_hoseichi(x_line), "-", color="k", label="内部レートによる補正値 (スコア 0 ライン)", zorder=2)
    ax.plot(x_line, get_hoseichi(x_line) + 0.1, "--", color="k", label="スコア ±10 ライン", zorder=2)
    ax.plot(x, y, ".", color="#1f77b4", label=f"補正値算出に使用したユーザー ({len(x):,} 人)", zorder=1)
    ax.plot(x_line, get_hoseichi(x_line) - 0.1, "--", color="k", zorder=1)

    cols = [
        "#808080",  # 灰
        "#804000",  # 茶
        "#008000",  # 緑
        "#00C0C0",  # 水
        "#0000FF",  # 青
        "#C0C000",  # 黄
        "#FF8000",  # 橙
        "#FF0000",  # 赤
    ]

    rate_min = min(min(x), rate2) - 50
    rate_max = max(max(x), rate2) + 50

    rates = [rate_min] + [i for i in range(400, 2801, 400)] + [rate_max]

    for i, col in enumerate(cols):
        plt.axvspan(rates[i] + 1, rates[i + 1] - 1, alpha=0.3, color=col, zorder=0)

    ax.set_xticks(np.arange((rate_min - 600) // 400 * 400, (rate_max + 600) // 400 * 400, 400))  # 400 の倍数
    ax.set_ylim(0, 1)
    ax.set_xlim(rate_min, rate_max)
    ax.set_xlabel("内部レート")
    ax.set_ylabel("平均順位率")
    ax.grid(c="#F0F0F0")
    ax.legend(loc="upper right")

    # StringIO を用いて画像を文字列として保存

    strio = StringIO()
    fig.savefig(strio, format="svg")
    plt.close(fig)

    strio.seek(0)
    contents = strio.getvalue()
    svgstr = contents[contents.index("<svg") :]

    return svgstr
