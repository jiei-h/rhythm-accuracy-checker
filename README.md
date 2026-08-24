# 🥁 Rhythm Accuracy Checker (Web Edition)

🔗 **Live Demo** [https://rhythm-accuracy-checker.onrender.com](https://rhythm-accuracy-checker.onrender.com)
> Note: Hosted on Render's free tier. The app may take up to 50 seconds to wake up if it has been inactive.

#### Description:
Rhythm Accuracy Checker is a modern web application designed for musicians and drum educators. It analyzes audio recordings of drum performances and quantifies timing accuracy by comparing hit onsets against a mathematically perfect tempo grid. 

Unlike basic analytical tools, this application converts raw timestamps into **musical notation (Bars & Beats)**, giving performers instant, intuitive feedback on exactly where they rushed or dragged in a song.

## ✨ Key Features
- **🌐 Intuitive Web UI:** Upload audio files and view analysis results instantly through a clean browser interface built with Flask.
- **🎼 Musician-Friendly Analysis:** Translates raw timing data into musical coordinates (e.g., *“Bar 4, Beat 2.5”*) rather than confusing seconds (e.g., *“12.45s”*).
- **📊 Time-Series Visualizations:** Generates a custom plot detailing every micro-timing deviation alongside a visual breakdown of your timing consistency ("Excellent", "Good", "Fair", "Poor" zones).
- **🧠 Dual-Metric Accuracy Evaluation:** Breaks timing accuracy down into **Tendency** (overall rushing/dragging habits) and **Stability** (unsteadiness and jitter), ensuring cancellation effects do not mask performance flaws.

## 🛠️ Project Architecture

The application has been refactored into a production-grade, modular package structure. This adheres to the Single Responsibility Principle, isolates temporary dynamic assets, and keeps the project clean and maintainable.

```text
rhythm-accuracy-checker/
│
├── data/                   # Dynamic runtime storage (Git-ignored)
│   ├── audio_files/        # Stores securely managed temporary user audio uploads
│   └── graphs/             # Caches dynamically generated time-series tempo graphs
│
├── docs/                   # Project documentation assets
│   └── images/             # Stores illustration screenshots used in this README
│
├── src/                    # Core Analytical Engine Package
│   ├── analysis/
│   │   └── metrics.py      # Computes statistics and maps raw seconds to Bars & Beats
│   ├── audio/
│   │   └── processor.py    # Manages audio signal loading and onset tracking via Librosa
│   ├── output/
│   │   └── report.py       # Handles rendering and saving matplotlib visual diagrams
│   └── exceptions.py       # Centralized hub for custom analytical exception handlers
│
├── static/                 # Fixed design assets (CSS stylesheets and UI templates)
├── templates/              # Jinja2 HTML blueprints for user interface dashboards
│   ├── index.html          # Web controller panel for multi-parameter session input
│   └── result.html         # Rich evaluation dashboard for displaying micro-timing results
│
├── tests/                  # Automated verification laboratory folder
│   └── test_project.py     # Contains isolated unit test suites using pytest engine
│
├── .gitignore              # Orchestrates deployment-ready file exclusion architecture
├── app.py                  # Main operational controller / Flask web server gatekeeper
├── drum_sample_174bpm.mp3  # Local verification reference audio (174 BPM 8th-note pattern)
├── drum_sample_87bpm.mp3   # Local verification reference audio (87 BPM 8th-note pattern)
├── pytest.ini              # Centralized configuration to streamline automated testing search paths
├── README.md               # Executive documentation and system architectural manual
└── requirements.txt        # Exact manifest pinning third-party module ecosystem
```

## 📂 Project Files Explained
- `app.py` - The main operational controller and entry point of the Web application. Handles Flask routing, multi-parameter user form data acquisition, and secure temporary file management.
- `src/` - The core analytical engine package, modularized for maximum readability and loose coupling:
  - `src/audio/processor.py` - Manages audio signal loading and tracks precision peak onsets using the `librosa` library.
  - `src/analysis/metrics.py` - The primary computational engine. Calculates micro-timing deviations, evaluates groove stability ratings, and mathematically maps raw timestamps into musical Bars & Beats.
  - `src/output/report.py` - Generates, renders, and caches the time-series visualization plots using `matplotlib`.
  - `src/exceptions.py` - Dictates centralized custom exception classes for robust error handling and platform reliability.
- `templates/` - Contains the structural Jinja2 HTML blueprints (`index.html` and `result.html`) for generating the frontend user dashboard.
- `static/` - Reserved repository folder designated for holding fixed presentation design sheets and structural assets.
- `data/` - Secure runtime scratchpad directory completely isolated from Git tracking via `.gitignore`:
  - `data/audio_files/` - Safely caches user drum recording tracks during analytical evaluation loops.
  - `data/graphs/` - Houses dynamically rendered tempo deviation graph outputs.
- `tests/` - The isolated continuous integration folder built explicitly for system validation routines:
  - `tests/test_project.py` - Harnesses `pytest` to execute unit tests, verifying the strict alignment of calculations, evaluations, and text formatting.
- `pytest.ini` - Centralized test suite configuration. Automatically binds the root path (`pythonpath = .`) to eliminate repetitive manual environment variables, optimizing developer workflows.
- `requirements.txt` - The exact environment manifest pinning the precise versions of the third-party dependency ecosystem.
- `drum_sample_174bpm.mp3`, `drum_sample_87bpm.mp3` - High-fidelity reference performance audio files targeted for system testing and developer verification.

## 🚀 How to Run Locally

### 1. Start the Flask Application Server
Run the web application by initiating the app controller script:
```bash
$ python3 app.py
```

### 2. Access the Application
Open your favorite web browser and navigate to the local development address:
```text
http://127.0.0.1:5000
```
Upload your drum track, punch in your target BPM and note value, and receive an instant structural breakdown of your groove precision.

## 📐 Design Decisions & Mathematical Breakdown
- **Pure Reference Grid Generation:** Relying on automated tempo tracking plugins can extract a grid corrupted by the human player's inherent fluctuations. This application forces user-defined target BPM constraints to ensure performance is compared against an unwavering, objective standard.
- **Conversion to Bars and Beats:** Humans do not think about tempo fluctuations in absolute time. By determining the time interval of a single note via $\text{Beat Duration} = \frac{60}{\text{BPM}} \times \frac{4}{\text{Time Denominator}}$, the system seamlessly map milliseconds back to bar divisions—greatly accelerating a player's practice efficiency.
- **Isolation of Data and Presentation:** Generated visualizations and temporary `.mp3`/`.wav` recordings are explicitly isolated inside the git-ignored `data/` directory. This keeps the deployment-ready codebase and the production workspace clean and unpolluted by local analytical debris.

## 📋 Limitations
- **Consistent Subdivision Assumptions:** The current analysis grid expects a uniform rhythm architecture throughout the runtime of the recording. Highly erratic rhythmic shifts (e.g., metric modulation or mid-song time signature changes) require further code extensions.
- **First-Onset Alignment Vulnerability:** To eliminate initial silence, the engine anchors the tempo grid to the very first detected onset (`onsets[0]`). However, if an unintended transient noise (e.g., mic handling, room ambience, breathing) is falsely captured as the first onset, the entire evaluation grid will shift out of phase, leading to skewed deviation results. Users must ensure their recordings have clean, noise-free intros.


## 📚 References
- Physics Today, ["Musical rhythms: The science of being slightly off"](https://aip.org)
- Friberg, A. and Sundberg, J. (1995), as cited in [Frontiers in Psychology](https://frontiersin.org)
