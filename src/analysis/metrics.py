import statistics
from dataclasses import dataclass
from src.exceptions import AudioProcessingError, InvalidInputError


EXCELLENT_THRESHOLD = 0.010
GOOD_THRESHOLD = 0.020
FAIR_THRESHOLD = 0.040


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
        raise AudioProcessingError("Sound detection failed")
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