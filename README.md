# Desktop Focus Helper

## 📚 Overview

**Desktop Focus Helper** is a lightweight, cross‑platform Python tool that runs locally on your computer and gently nudges you back to work when you start to drift. It monitors:

- **Keyboard activity** (keystrokes per minute)
- **Mouse movement** (moves per minute)
- **Active window title** (e.g., which application you’re using)
- *(optional stub)* Browser tab URLs

When activity falls below a configurable threshold, the application plays a short audio cue (e.g., “You’re drifting!”). When you recover activity, it celebrates with an encouraging cue (e.g., “Great job!”). No manual status tracking—just real‑time audible feedback.

---

## 🎯 Goals & Immediate Value

- **Instant awareness** of unproductive moments.
- **Non‑intrusive**, short audio signals keep the workflow smooth.
- **Zero external services** – everything runs locally.
- **Extensible** – add richer window/tab detection or custom sounds later.

---

## 🛠️ Technologies

| Component | Reason for Choice |
|-----------|-------------------|
| **Python 3.11** | Batteries‑included, cross‑platform, easy to ship in a Docker container. |
| **typer** | Simple declarative CLI; automatic `--help` generation. |
| **pynput** | Pure‑Python listeners for keyboard and mouse on Windows/macOS/Linux. |
| **psutil** | Process & system utilities (active window titles, process names). |
| **playsound** | Plays WAV/MP3 files without heavy audio back‑ends. |
| **webbrowser / selenium‑wire** | Stub for future browser‑tab detection (replaceable later). |
| **yaml** | Human‑readable configuration file. |

---

## 📂 Repository Structure

```
project/
├─ focus_helper.py      # Entry point – Typer CLI
├─ monitor.py           # Core activity collector
├─ audio.py             # Thin wrapper around playsound
├─ config.yaml          # Default thresholds & audio paths
├─ assets/
│   ├─ alert.wav        # “You’re drifting!” cue
│   └─ cheer.wav        # “Great job!” cue
├─ requirements.txt
└─ project_plan.txt
```

*All source files live in the repository root; no hidden directories.*

---

## 📦 Installation

> **Prerequisite:** Python 3.11 (or newer) must be available on your machine.

1. **Clone the repo**

   ```bash
   git clone https://github.com/your‑org/desktop-focus-helper.git
   cd desktop-focus-helper
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. *(Optional)* **Docker** – for isolated testing

   ```bash
   docker build -t desktop-focus-helper:latest .
   docker run --rm -it --device /dev/snd -v $(pwd):/app desktop-focus-helper
   ```

   > The container must have audio device access (`--device /dev/snd`) to play sounds on the host.

---

## 🚀 Quick Start

### 1. Run the Demo

```bash
python focus_helper.py demo
```

- Simulates a low‑activity period.
- Prints live stats.
- Triggers an **alert** sound followed by a **cheer** sound.

### 2. Real Monitoring

```bash
python focus_helper.py start
```

- Begins listening to keyboard/mouse and active‑window polling.
- Every 5 seconds prints a summary: `keystrokes/min`, `mouse moves/min`, `active window`.
- When activity drops below the `low_activity_threshold` (default 30 s) → **alert** sound.
- When activity rises above the `recovery_threshold` → **cheer** sound.

Press `Ctrl‑C` to stop.

### 3. Stop Command (for completeness)

```bash
python focus_helper.py stop
```

> In the current implementation the `stop` command simply exists for future integration (e.g., system‑service mode). The interactive `start` command handles termination via `Ctrl‑C`.

---

## ⚙️ Configuration (`config.yaml`)

```yaml
# thresholds (per minute)
keystrokes_per_min_low: 10         # below this → distraction
mouse_moves_per_min_low: 20        # below this → distraction
low_activity_duration: 30          # seconds of sustained low activity before alert

activity_recovery_threshold: 30    # percent increase to trigger cheer

# audio files (relative to repo root)
alert_sound: "assets/alert.wav"
cheer_sound: "assets/cheer.wav"

# polling
poll_interval_seconds: 1
stats_report_interval_seconds: 5
```

- Adjust thresholds to match your workflow.
- Replace `alert.wav` / `cheer.wav` with any short audio of your choice (WAV or MP3).
- All paths are relative to the repository root; you may also use absolute paths.

---

## 🎧 Audio Handling

`audio.play_sound(path)` attempts to play the given file using **playsound**. If audio playback fails (e.g., container without audio device), it automatically **falls back to a console stub**:

```
[AUDIO: assets/alert.wav]
```

The fallback guarantees that the rest of the program continues to work and provides a visible cue in logs.

---

## 🛠️ Core Modules Explained

### `monitor.py`

```python
class ActivityMonitor:
    def __init__(self, cfg: dict) -> None
    def start(self) -> None
    def stop(self)  -> None
    def get_stats(self) -> dict
```

- Uses **pynput** listeners for keyboard & mouse.
- Spawns a background thread polling **psutil** (or `win32gui` on Windows) each `poll_interval_seconds`.
- Returns stats: `{keystrokes_per_min, mouse_moves_per_min, active_window}`.

### `audio.py`

```python
def play_sound(path: str) -> None
def alert() -> None          # plays config['alert_sound']
def cheer() -> None          # plays config['cheer_sound']
```

- Wrapper abstracts fallback logic.

### `focus_helper.py`

- Typer CLI exposing three commands: `start`, `demo`, `stop`.
- Loads configuration via `load_config()`.
- Implements the decision logic that decides when to call `audio.alert()` or `audio.cheer()` based on activity trends.

---

## 📋 Testing & Verification

1. **Import check**

   ```python
   >>> from monitor import ActivityMonitor
   >>> am = ActivityMonitor({})
   >>> am.get_stats()
   {'keystrokes_per_min': 0, 'mouse_moves_per_min': 0, 'active_window': 'python.exe'}
   ```

2. **Audio stub**

   ```python
   >>> from audio import alert
   >>> alert()   # prints [AUDIO: assets/alert.wav] if playback fails
   ```

3. **Demo script**

   ```bash
   $ python focus_helper.py demo
   ```

   - Output includes live stats.
   - Should hear (or see) both audio cues.

4. **Real monitoring**

   ```bash
   $ python focus_helper.py start
   # Observe stats printed every 5 seconds.
   # After simulated inactivity, you should hear the alert.
   ```

---

## 📈 Future Enhancements

- **Browser tab detection** – integrate Selenium or browser extensions to capture URLs and flag “known distracting sites”.
- **OS‑specific window titles** – use `win32gui` on Windows, `AppKit` on macOS for crisp titles.
- **Desktop notifications** – complement audio with subtle OS notifications.
- **Persistence** – store activity logs for long‑term trend analysis.
- **System‑service mode** – run in background as a daemon/service.

---

## 🤝 Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/awesome-feature`.
3. Add/modify code. Ensure `black` and `flake8` pass via `make lint`.
4. Write and run unit tests (`pytest`).
5. Open a Pull Request with a clear description and link to related issue.

> All contributions must be compatible with the MIT license.

---

## 📜 License

This project is licensed under the **MIT License** – see the `LICENSE` file for details.

---

## ✉️ Contact & Support

- **Maintainer:** Your Name (<you@example.com>)
- **Issues:** Please file bug reports or feature requests via the GitHub repository's *Issues* tab.

--- 

*Happy focusing!*
