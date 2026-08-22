import statistics
from dataclasses import dataclass
from src.exceptions import AudioProcessingError


EXCELLENT_THRESHOLD = 0.010
GOOD_THRESHOLD = 0.020
FAIR_THRESHOLD = 0.040


#  演奏者向けに「第何小節、何拍目」という文字列受け取れるように変更
@dataclass
class DeviationSummary:
    average: float
    stdev: float
    extreme: float
    extreme_time: str
    judgment: str

    def as_text(self):
        return (
            f"Tendency: {self.average:.3f}s\n"
            f"Stability: {self.stdev:.3f}s ({self.judgment})\n"
            f"Max Deviation: {self.extreme:.3f}s (at {self.extreme_time})"
        )
        

def calculate_deviations(bpm, time_num, time_den, onsets):
    # 1. 拍の長さを計算
    # 4/4 なら60/bpm、6/8 なら30/bpmに切り替わる
    beat_duration = 60 / bpm * (4 / time_den)
    
    # １小節の長さ（秒数）
    # 4/4で一拍が0.5秒なら、1小節は2秒。6/8で１拍が0.25秒なら、１小節は1.5秒。
    measure_duration = beat_duration * time_num
   
    deviations = []
    for onset in onsets:
        # 2. 音の秒数を「通算で何小節か」に変換
        total_measures = onset / measure_duration
        
        # 3. 音源における１番細かいグリッド（例：16分音符）に変換
        # ここでは、１拍をさらに細かく分割したグリッドに変換するため、time_numを掛ける
        subdivision = 4
        grid_per_measure = time_num * subdivision
        
        # 4. 最も近いグリッドの位置を計算
        closest_grid = round(total_measures * grid_per_measure)
        
        # 5. ジャストのグリッドからのズレを計算、秒数に変換
        just_time = (closest_grid / grid_per_measure) * measure_duration
        time_diff = onset - just_time
        
        deviations.append(time_diff)
    
    return deviations


# 演奏者に親切な形で、最大ズレの発生箇所を「第何小節、何拍目」として返すように変更
def summarize(deviations, onsets, bpm, time_num, time_den):
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
    
    # 5. 最大ズレ発生の箇所（秒数）を「第何小節、何拍目」に分解
    beat_duration = (60 / bpm) * (4 / time_den)
    total_beats = extreme_time / beat_duration
    
    # 割り算の商から小節数を、余りから拍数を計算
    bar_number = int(total_beats // time_num) + 1
    beat_number = (total_beats % time_num) + 1
    
    # 画面表示のためのテキストにする
    extreme_time_text = f"Bar {bar_number}, Beat {beat_number:.1f}"

    return average, stdev, extreme, extreme_time_text


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