# Rhythm Accuracy Checker

🔗 [Live Demo](https://rhythm-accuracy-checker.onrender.com) ・ [GitHub](https://github.com/jiei-h/rhythm-accuracy-checker)

> ※ Renderの無料プランでホスティングしているため、一定時間アクセスがないとスリープします。初回アクセス時は起動に最大50秒程度かかることがあります。

## 1. 概要

演奏していると、メトロノームより少し早く、あるいは遅く叩いてしまうことがあります。感覚的には「少しズレている」と分かっていても、実際にどのくらいズレているのか、またそのブレにどのような傾向があるのかは、感覚だけでは把握しにくいと感じました。そこで、自分の演奏のタイミングを数値化して可視化することで、普段の演奏では気づきにくいブレや傾向を客観的に確認し、より効果的な練習や演奏力の向上につなげたいと考え、このアプリを開発しました。

Rhythm Accuracy Checkerは、演奏音源から打点(onset)のタイミングを分析し、リズムの正確さ・タイミングの傾向・安定性を定量評価するWebアプリケーションです。

## 2. デモ

![解析結果の画面例](docs/images/example_output.png)

音源をアップロードし、目標BPM・拍子・音符の刻みを指定すると、タイミングのズレを時系列グラフと数値で確認できます。

## 3. 主な機能

- 音源ファイルのアップロード
- BPM・拍子・音符単位の指定
- Onset Detectionによる打点検出
- 基準グリッドとのTiming Deviation算出
- Timing Tendency(早まる/遅れる傾向)の表示
- Timing Stability(タイミングの安定性)の評価
- 分析結果のグラフ表示

## 4. 開発時に直面した課題と対応

### 4.1 Dockerデプロイ後の音源処理エラー

RenderへのデプロイをDocker環境に切り替えた後、音源ファイルをアップロードして分析を実行すると、`Internal Server Error`が発生する問題がありました。

まず原因を特定するためにRenderのログを確認したところ、プロセスが`SIGKILL`で終了しており、`Perhaps out of memory?`というメッセージが出ていました。さらに詳細なログを確認すると、`handle_abort`に関する記録もあり、単純なアプリケーション側の例外ではなく、処理中にプロセスが強制終了されている可能性があると考えました。

そこで、音声処理にかかる時間と実行環境を調べた結果、`gunicorn`のデフォルトタイムアウトが30秒であること、Renderの無料プランではCPUリソースが限られていること、さらに`librosa`が依存する`numba`の初回JITコンパイルによって、初回の音声処理に時間がかかることが分かりました。これらの条件が重なり、初回の音源処理が30秒以内に完了せず、`gunicorn`によってワーカーが終了させられていることが原因だと判断しました。

対応として、`gunicorn`の起動オプションに`--timeout 120`を追加し、音声処理に十分な実行時間を確保しました。その結果、Docker環境でも音源アップロードから分析処理まで正常に実行できるようになりました。

この経験から、アプリケーションのコードだけでなく、音声処理の計算量・依存ライブラリの初期処理・Webサーバーのタイムアウト・デプロイ先のリソース制約を含めて、実行環境全体を考慮する必要があることを学びました。

<details>
<summary>実際のエラーログ(クリックで展開)</summary>

```text
File ".../numba/core/typed_passes.py", line 648, in run_pass
    if guard(workfn, state, work_list, block, i, expr,
...
File ".../gunicorn/workers/base.py", line 204, in handle_abort
    sys.exit(1)
SystemExit: 1
[2026-08-28 08:54:53 +0000] [49] [INFO] Worker exiting (pid: 49)
[2026-08-28 08:54:54 +0000] [6] [ERROR] Worker (pid:49) was sent SIGKILL! Perhaps out of memory?
[2026-08-28 08:54:55 +0000] [69] [INFO] Booting worker with pid: 69
```

</details>

### 4.2 その他の対応

- **matplotlibのバックエンド問題**: `matplotlib.pyplot`をインポートする前に`matplotlib.use("Agg")`を呼ばないと、Flaskのメインスレッド外での描画でクラッシュしていたため、インポート順序を固定して解消した
- **AirPlayとのポート競合**: MacのAirPlayレシーバーがデフォルトでポート5000を使用しており、Flaskの開発サーバーが起動できなかったため、システム設定でAirPlayレシーバーを無効化した
- **複数AI並行編集によるコンフリクト**: 複数のAIアシスタントを並行して同じコードベースの改修に使った際に、意図しない競合が発生したため、作業開始前に`git pull origin main` → `pytest` → 手動での動作確認、という3ステップのルールを設けた
- **`$PORT`展開のためのシェル形式CMD**: Dockerの`CMD`で環境変数`$PORT`を正しく展開するには、配列形式ではなくシェル形式で書く必要があると分かり、シェル形式を採用した

## 5. 分析ロジックと評価設計

```text
Audio
  ↓
Onset Detection
  ↓
基準グリッド生成
  ↓
Timing Deviation
  ↓
統計分析
  ↓
Timing Tendency / Stability
  ↓
Visualization
```

### 5.0 基準グリッドの設計

**What**
ユーザーが入力したBPMと拍子、指定した音符単位(`note_value`)をもとに、演奏タイミングを評価するための基準グリッドを生成します。

**Why**
このアプリの目的は、曲そのもののテンポを自動推定することではなく、ユーザーが指定したテンポに対して、演奏がどの程度正確だったかを評価することです。そのため、BPMを自動推定するのではなく、ユーザー自身がBPMを指定する設計にしています。これにより、「推定されたテンポに対してズレている」のではなく、ユーザーが意図したテンポを基準として演奏タイミングを評価できます。

### 5.1 Onset Detection

**What**
入力された音源から、音が発生したタイミング(onset)を検出し、演奏における各打点の時刻として利用します。

**Why**
演奏のリズムを数値化するためには、まず「演奏者がいつ音を鳴らしたのか」を時刻として取得する必要があります。そこで、音源から検出したonsetを基準グリッドと比較することで、各打点が本来のタイミングからどの程度ズレているのかを算出できるようにしています。

### 5.2 Timing Deviation

検出したonsetを、BPMと拍子、指定した音符単位(`note_value`)から生成した基準グリッドと比較し、最も近いグリッド位置との時間差を算出します。

単純に4分音符単位のグリッドだけを使用すると、8分音符の裏拍など、本来演奏すべき細かいタイミングが評価対象から外れてしまいます。そのため、指定した音符の細かさに合わせてグリッドを分割し、実際の演奏位置に対応した基準と比較しています。

```text
Timing Deviation = Actual Onset - Nearest Grid Time
```

正の値は基準グリッドより遅く、負の値は基準グリッドより早いことを表します。

### 5.3 Timing Tendency

**What**
各onsetについて算出したTiming Deviationの平均値(`average`)を求め、演奏全体が基準グリッドに対してどちら側にズレる傾向があるかを、符号付きの数値として表示します。

```text
average > 0  → 基準より遅れる傾向
average < 0  → 基準より早まる傾向
```

例えば、`+0.015s`であれば平均して15ms遅く、`-0.008s`であれば平均して8ms早いことを表します。

**Why**
個々の打点のズレだけを見るのではなく、Timing Deviationの平均値を見ることで、演奏全体が基準に対して早まる傾向なのか、遅れる傾向なのかを把握できるようにしています。

なお、現在の実装では、この数値を`Rushing`や`Dragging`というカテゴリに自動分類する処理は行っていません。符号付きの平均値をそのまま表示することで、ユーザー自身が早い・遅いという傾向を読み取れる設計としています。

### 5.4 Stability

**What**
Timing Deviationのばらつきを統計的に評価し、演奏タイミングがどの程度安定しているかを確認します。

**Why**
平均的なズレが小さくても、各打点のタイミングが大きくばらついていれば、安定した演奏とは言えません。

例えば、ある演奏で平均的なTiming Deviationがほぼ0msだったとしても、

```text
-30ms → +25ms → -20ms → +30ms
```

のように毎回大きく揺れている場合と、

```text
+3ms → +5ms → +4ms → +2ms
```

のようにほぼ一定している場合では、演奏の安定性は大きく異なります。そのため、平均的なズレとは別にTiming Deviationのばらつき(標準偏差)を評価し、演奏タイミングの安定性を確認しています。

### 5.5 評価設計

Timing Deviationの大きさをもとに、演奏タイミングを`Excellent`、`Good`、`Fair`、`Poor`の4段階で評価します。現在の評価基準は以下の通りです。

| Timing Deviation(標準偏差) | Evaluation |
| --------------------------- | ---------- |
| 10ms以下                     | Excellent  |
| 10msを超え20ms以下            | Good       |
| 20msを超え40ms以下            | Fair       |
| 40msを超える                  | Poor       |

これらの閾値は、タイミング知覚やマイクロタイミングに関する研究・文献を参考に設定しています。ただし、**10ms・20ms・40msという区切り自体が学術的に確立された評価基準ではありません。** そのため、本アプリでは研究上の知見を参考にしながら、演奏結果を段階的に評価するための**独自の目安値**として使用しています。

今後は、実際の演奏データを用いた検証や、より多くの研究結果との比較を通して、評価基準の妥当性を検討していきます。

## 6. 技術スタックとアーキテクチャ

### 技術スタック

| Category           | Technology |
| ------------------ | ---------- |
| Language            | Python 3.12(ローカル) / 3.9(Dockerイメージ) |
| Web Framework       | Flask 3.1.3 |
| Web Server          | Gunicorn 23.0.0(ローカル検証時) |
| Audio Analysis      | librosa 0.11.0 |
| Numerical Analysis  | NumPy 2.0.2 |
| Audio I/O           | soundfile 0.13.1 |
| Visualization       | Matplotlib 3.9.4 |
| Testing             | pytest |
| Container           | Docker |
| Deployment          | Render(Dockerデプロイ) |

### アーキテクチャ

```text
Browser
   ↓
Flask (app.py)
   ↓
Audio Processing (src/audio/processor.py)
   ↓
Analysis Logic (src/analysis/metrics.py)
   ↓
Visualization (src/output/report.py)
   ↓
Browser
```

## 7. ディレクトリ構成

```text
rhythm-accuracy-checker/
├── data/                    # 実行時に生成される一時データ(Git管理外)
│   ├── audio_files/         # アップロードされた音源の一時保存先
│   └── graphs/               # 生成したタイミング解析グラフの保存先
├── docs/images/              # READMEに掲載するスクリーンショット
├── src/
│   ├── audio/processor.py    # librosaによる音源読み込み・onset検出
│   ├── analysis/metrics.py   # Timing Deviation計算、Tendency/Stability評価
│   ├── output/report.py      # matplotlibによるグラフ生成
│   └── exceptions.py         # 独自例外クラス
├── templates/                 # Flaskのビュー(index.html / result.html)
├── static/style.css
├── tests/test_project.py      # pytestによる単体テスト
├── app.py                     # Flaskエントリーポイント
├── Dockerfile
├── .dockerignore
├── requirements.txt
└── pytest.ini
```

## 8. セットアップ・環境構築

### Requirements

- Python 3.9以上
- pip
- Docker(Dockerで動かす場合)

### ローカル環境(venv)

```bash
git clone https://github.com/jiei-h/rhythm-accuracy-checker.git
cd rhythm-accuracy-checker

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
python3 app.py
```

`http://127.0.0.1:5000` にアクセスして動作を確認します。

### Docker

```bash
docker build -t rhythm-accuracy-checker .
docker run -p 8000:8000 -e PORT=8000 rhythm-accuracy-checker
```

`http://127.0.0.1:8000` にアクセスして動作を確認します。

### デプロイ(Render)

Renderのダッシュボードで、対象サービスの Settings → Build → Source から Runtime を `Docker` に切り替えることで、リポジトリ内の `Dockerfile` を使ったビルド・デプロイが自動的に行われます。ポートはRenderが注入する`PORT`環境変数を`Dockerfile`内の`gunicorn`起動コマンドがそのまま利用します。

## 9. テスト

`src/analysis/metrics.py` の計算ロジックを中心に、pytestで単体テストを実装しています。

```bash
pytest
```

`pytest.ini` に `pythonpath = .` を設定しているため、`PYTHONPATH` の手動設定は不要です。

## 10. 今後の課題・改善点

### 現在の制約

- **拍子・音符単位が曲中で変化する演奏への非対応**: 現状は演奏全体を通して単一の拍子・音符単位という前提でグリッドを生成しているため、例えば8分音符から16分音符へ刻みが変化するような演奏では、検出結果にズレが生じる
- **先頭オンセットのノイズ耐性**: 無音区間をスキップするため最初に検出されたオンセット(`onsets[0]`)を基準にグリッドを生成しており、マイクのハンドリングノイズ等を誤検出すると解析全体がズレる可能性がある
- **評価閾値の妥当性**: `Excellent`〜`Poor`の閾値は独自設定であり、実際の演奏データでの検証が不十分

### 今後の改善

- 曲中で拍子・音符単位が変化するケースへの対応
- 先頭オンセット検出のノイズ耐性向上
- より多様な演奏データを用いた評価閾値の妥当性検証
- CI/CDパイプライン(GitHub Actions等)の整備

## 参考文献

- Physics Today, "Musical rhythms: The science of being slightly off" (https://aip.org)
- Friberg, A. and Sundberg, J. (1995), as cited in Frontiers in Psychology (https://frontiersin.org)