import sys
import librosa
import statistics
from statistics import StatisticsError
from soundfile import LibsndfileError
import matplotlib.pyplot as plt
from dataclasses import dataclass


EXCELLENT_THRESHOLD = 0.010
GOOD_THRESHOLD = 0.020
FAIR_THRESHOLD = 0.040

OUTPUT_GRAPH_FILENAME = "tempo_graph.png"


@dataclass
class DeviationSummary:
    average: float
    stdev: float
    extreme: float
    extreme_time: float
    judgment: str

    def as_text(self):
        return (
            f"Tendency: {self.average:.3f}s\n"
            f"Stability: {self.stdev:.3f}s ({self.judgment})\n"
            f"Max Deviation: {self.extreme:.3f}s (at {self.extreme_time:.3f}s)"
        )


def main():
    # inputを受け取る(基準BPM、基準音符、音源ファイル)
    filename, bpm, note_value = get_user_input()
    # 結果(graph, image, summary)を出力
    try:
        y, sr = load_audio(filename)
    except LibsndfileError:
        sys.exit("File does not exist, is corrupted or, is not a supported format")

    duration = get_duration(y, sr)
    onsets = onset_detect(y, sr)
    deviations = calculate_deviations(bpm, note_value, onsets, duration)

    try:
        average, stdev, extreme, extreme_time = summarize(deviations, onsets)
    except StatisticsError:
        sys.exit("Sound detection failed")
        
    judgment = evaluate_stability(stdev)
    summary = DeviationSummary(average, stdev, extreme, extreme_time, judgment)

    plot_deviation(onsets, deviations, summary)

    print(summary.as_text())
    print(f"Graph saved to {OUTPUT_GRAPH_FILENAME}")


def get_user_input():
    filename = input("File Name: ")
    try:
        bpm = float(input("BPM: "))
    except ValueError:
        sys.exit("BPM must be a number")
    if bpm <= 0:
        sys.exit("BPM must be a positive number")

    try:
        note_value = float(input("Note Value: "))
    except ValueError:
        sys.exit("Note Value must be a number")
    if note_value not in [4, 8, 16, 32]:
        sys.exit("Note Value must be one of: 4, 8, 16, 32")

    return filename, bpm, note_value


def load_audio(filename):
    # ファイルを読み込む
    y, sr = librosa.load(filename)
    return y, sr


def get_duration(y, sr):
    duration = librosa.get_duration(y=y, sr=sr)
    return duration


def onset_detect(y, sr):
    # タイミングを検出
    onsets = librosa.onset.onset_detect(y=y, sr=sr, units="time")
    return onsets

# 基準とのズレを計算


def calculate_deviations(bpm, note_value, onsets, duration):
    # 基準のグリッドを計算し作成
    subdivision = note_value / 4
    beat_interval = (60 / bpm) / subdivision
    grids = []
    t = 0
    while t < duration:
        grids.append(t)
        t += beat_interval
    # 基準から演奏のオンセットのズレを計算
    deviations = []
    for onset in onsets:
        closest = min(grids, key=lambda grid: abs(grid - onset))
        diff = onset - closest
        deviations.append(diff)
    return deviations


def summarize(deviations, onsets):
    if len(deviations) < 2:
        raise StatisticsError("Sound detection failed")
    # 傾向(Rushing/Dragging)
    average = statistics.mean(deviations)
    # 安定性(ズレのばらつき)
    stdev = statistics.stdev(deviations)

    # 最大ズレの大きさ
    extreme = max(deviations, key=abs)
    # 最大ズレ発生の箇所
    extreme_index = deviations.index(extreme)
    # 最大ズレ発生の時間
    extreme_time = onsets[extreme_index]

    return average, stdev, extreme, extreme_time


def evaluate_stability(stdev):
    # ズレから「安定」「やや不安定」などを判定
    # 閾値は秒単位（summarize()が返すstdevと単位を揃える）
    # 参考文献に基づく目安値。学術的に確立された基準ではなく独自設定。
    if stdev <= EXCELLENT_THRESHOLD:      # 10ms以下
        return "Excellent!"
    elif stdev <= GOOD_THRESHOLD:    # 10ms-20ms
        return "Good"
    elif stdev <= FAIR_THRESHOLD:    # 20ms-40ms
        return "Fair"
    else:                   # 40ms以上
        return "Poor"


def plot_deviation(onsets, deviations, summary, graph_filename=OUTPUT_GRAPH_FILENAME):
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


if __name__ == "__main__":
    main()
