import librosa
from soundfile import LibsndfileError
from src.exceptions import AudioProcessingError # src/exceptions.py から AudioProcessingError をインポート


def load_audio(filename): # ファイルを読み込む
    try:
        y, sr = librosa.load(filename)
        return y, sr
    except LibsndfileError:
        raise AudioProcessingError("File does not exist, is corrupted or, is not a supported format")


def get_duration(y, sr): # 音源の長さを取得
    duration = librosa.get_duration(y=y, sr=sr)
    return duration


def onset_detect(y, sr): # タイミングを検出
    onsets = librosa.onset.onset_detect(y=y, sr=sr, units="time")
    return onsets
