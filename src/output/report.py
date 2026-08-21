import matplotlib
matplotlib.use("Agg")  # GUIを使わずにグラフを生成
import matplotlib.pyplot as plt

# 計算ロジック側で定義した定数をインポートして使う
from src.analysis.metrics import EXCELLENT_THRESHOLD, GOOD_THRESHOLD


def plot_deviation(onsets, deviations, summary, graph_filename):
    # 時系列でグラフ化
    plt.figure(figsize=(12, 4))
    plt.axhline(y=0, color="red", linewidth=1.5)
    plt.axhspan(-EXCELLENT_THRESHOLD, EXCELLENT_THRESHOLD, color="green",
                alpha=0.15, label="Excellent zone(+-10ms)")
    plt.axhspan(EXCELLENT_THRESHOLD, GOOD_THRESHOLD, color="yellow", alpha=0.15)
    plt.axhspan(-GOOD_THRESHOLD, -EXCELLENT_THRESHOLD,
                color="yellow", alpha=0.15, label="Good zone(+-20ms)")
    plt.plot(onsets, deviations, color="steelblue", marker="o", markersize=3, linewidth=1)

    plt.gcf().text(0.02, 0.88, summary.as_text(), fontsize=9,
                   bbox=dict(facecolor="white", alpha=0.7))

    plt.xlabel("Time(s)")
    plt.ylabel("Deviation(s)")
    plt.title("Tempo Deviation Over Time")
    plt.legend(loc="upper right")
    plt.savefig(graph_filename)
