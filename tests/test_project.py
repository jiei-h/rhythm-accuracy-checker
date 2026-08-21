from project import evaluate_stability, summarize, calculate_deviations
from pytest import approx


def test_evaluate_stability():
    assert evaluate_stability(0.005) == "Excellent!"
    assert evaluate_stability(0.010) == "Excellent!"  # 境界値ちょうど
    assert evaluate_stability(0.015) == "Good"
    assert evaluate_stability(0.020) == "Good"  # 境界値ちょうど
    assert evaluate_stability(0.025) == "Fair"
    assert evaluate_stability(0.040) == "Fair"  # 境界値ちょうど
    assert evaluate_stability(0.050) == "Poor"


def test_summあrize():
    deviations = [0.01, -0.01, 0.03]
    onsets = [1.0, 2.0, 3.0]
    average, stdev, extreme, extreme_time = summarize(deviations, onsets)
    assert average == approx(0.01)
    assert extreme == approx(0.03)
    assert extreme_time == approx(3.0)
    assert stdev == approx(0.02)


def test_calculate_deviations():
    bpm = 60
    note_value = 4
    onsets = [0.1, 1.9, 2.4]
    duration = 3
    deviations = calculate_deviations(bpm, note_value, onsets, duration)
    assert deviations == approx([0.1, -0.1, 0.4])


