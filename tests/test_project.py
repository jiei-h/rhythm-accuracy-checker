import pytest
from src.analysis.metrics import evaluate_stability, summarize, calculate_deviations

# 1. ズレ計算テスト
def test_calculate_deviations():
    bpm = 120
    time_num = 4
    time_den = 4
    note_value = 16  # 16分音符刻み（1拍を4分割）
    # 最初の音（0.125秒が16分音符のジャスト）に、あえて0.01秒の「ズレ」を混ぜた [0.135] 
    onsets = [0.135, 0.5, 1.0, 1.5, 2.0]  # 仮のオンセットタイミング（秒）
    
    deviations = calculate_deviations(bpm, time_num, time_den, note_value, onsets)
    
    # ズレの長さが正しいかを確認（ここでは仮の期待値を使用）
    assert len(deviations) == len(onsets)
    assert all(isinstance(dev, float) for dev in deviations)
    assert deviations[0] == pytest.approx(0.01, abs=1e-5)

# 2. summarize関数のテスト
def test_summarize():
    deviations = [0.01, 0.02, -0.01]
    onsets = [0.0, 0.5, 1.0]
    bpm = 120
    time_num = 4
    time_den = 4
    
    # 最大のズレは 0.02で、発生箇所は2番目のオンセット（0.5秒）１小節目の2拍目
    average, stdev, extreme, extreme_time_text = summarize(deviations, onsets, bpm, time_num, time_den)
    
    # 浮動小数点の細かい計算になるため、pytest.approx を使って厳密にチェックします
    assert average == pytest.approx(0.006666666666666667, abs=1e-5)
    assert stdev == pytest.approx(0.015275252316519467, abs=1e-5)
    assert extreme == pytest.approx(0.02, abs=1e-5)
    assert extreme_time_text == "Bar 1, Beat 2.0" # 文字列が正しいかを確認
    
# 3. evaluate_stability関数のテスト
def test_evaluate_stability():
    # 安定性の評価が正しいかを確認するためのテストケース
    assert evaluate_stability(0.005) == "Excellent!"
    assert evaluate_stability(0.015) == "Good"
    assert evaluate_stability(0.030) == "Fair"
    assert evaluate_stability(0.050) == "Poor"
    
