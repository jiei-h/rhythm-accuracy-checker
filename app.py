from flask import Flask, render_template, request
import uuid
from project import load_audio, get_duration, onset_detect, calculate_deviations, summarize, evaluate_stability, DeviationSummary

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    audio_file = request.files["audio_file"]
    unique_filename = f"{uuid.uuid4()}_{audio_file.filename}"
    audio_file.save(unique_filename)
    bpm = int(request.form["bpm"])
    note_value = int(request.form["note_value"])

    y, sr = load_audio(unique_filename)
    duration = get_duration(y, sr)
    onsets = onset_detect(y, sr)
    deviations = calculate_deviations(bpm, note_value, onsets, duration)
    average, stdev, extreme, extreme_time = summarize(deviations, onsets)
    judgment = evaluate_stability(stdev)
    summary = DeviationSummary(average, stdev, extreme, extreme_time, judgment)

    return render_template("result.html", audio_file=audio_file, bpm=bpm, note_value=note_value, summary=summary)


if __name__ == "__main__":
    app.run(debug=True)