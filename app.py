import os
import uuid
from flask import Flask, render_template, request, send_from_directory
from src.audio.processor import load_audio, get_duration, onset_detect
from src.analysis.metrics import calculate_deviations, summarize, evaluate_stability, DeviationSummary
from src.output.report import plot_deviation
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    audio_file = request.files["audio_file"]
    
    # アップロードされた音源を　data/audio_files/ に保存する
    unique_filename = f"{uuid.uuid4()}_{audio_file.filename}"
    audio_save_path = os.path.join("data/audio_files", unique_filename)
    audio_file.save(audio_save_path)
    
    # フォームからBPMを受け取る
    bpm = int(request.form["bpm"])
    
    # フォームから拍子（分子・分母）を受け取る
    time_num = int(request.form["time_num"])
    time_den = int(request.form["time_den"])
    #フォームから音符の種類を受け取る
    note_value = int(request.form["note_value"])

    # 音源を読み込み、解析を行う
    y, sr = load_audio(audio_save_path)
    duration = get_duration(y, sr)
    onsets = onset_detect(y, sr)
    
    deviations, first_onset = calculate_deviations(bpm, time_num, time_den, note_value, onsets)
    average, stdev, extreme, extreme_time_text = summarize(deviations, onsets, bpm, time_num, time_den, first_onset)
    
    judgment = evaluate_stability(stdev)
    summary = DeviationSummary(average, stdev, extreme, extreme_time_text, judgment)
    

    # グラフを生成し、保存する
    graph_filename = f"{uuid.uuid4()}_tempo_graph.png"
    graph_path = os.path.join("data", "graphs", graph_filename)
    plot_deviation(onsets, deviations, summary, graph_path)

    return render_template("result.html", audio_file=audio_file, bpm=bpm, note_value=note_value, time_num=time_num, time_den=time_den, summary=summary, graph_filename=graph_filename)


# data/graphs/ の中の画像を画面に表示するためのルート（実務の定番テクニック）
@app.route("/images/<filename>")
def serve_graph(filename):
    # data/graphs フォルダの中から、指定されたファイル名の画像を安全に画面へ返します
    return send_from_directory(os.path.join("data", "graphs"), filename)


if __name__ == "__main__":
    app.run(debug=True)