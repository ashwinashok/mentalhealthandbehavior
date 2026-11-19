# AttentionSpan

AttentionSpan is an IRB-approved EEG study of how mobile notifications interrupt ongoing attention. People do timed cognitive tasks while we record brain activity. On some sittings a text or ping arrives; on others it does not. The question is whether leftover brain activity, behavior, and (when recorded) heart rate change after that interruption, and whether they return.

This repository is **code only**. Participant recordings, survey exports, wearable exports, plots, and scored results are not in git. Those files live on the lab machine and in the project’s Teams folders.

## What we measure

Each sitting is one of four conditions:

| Set | Condition |
|-----|-----------|
| 1 | Baseline — no phone |
| 2 | Text arrives; the participant may reply |
| 3 | Text arrives; glance only, no reply |
| 4 | Auditory ping; eyes stay on the task |

Study 1 used three sets (1–3) with a consumer headband and scored behavior, EEG recovery, surveys, and watch-based heart rate. Study 2 keeps the same tasks and adds set 4, 16-channel EEG, and optional ECG from the board during the same sitting.

We do not treat a bump on a leftover plot as a named ERP (P300, N400, and so on) unless that pattern both repeats and differs by condition.

## Two collection setups

Hardware and run-day steps are **not** in this README. Use the matching tutorial:

- [Muse_Setup.md](Muse_Setup.md) — Study 1 headband, LSL, PsychoPy tasks, XDF/CSV
- [OpenBCI_Setup.md](OpenBCI_Setup.md) — Study 2 Cyton+Daisy, GUI recording, markers, notebooks, ECG

The older Word write-up `Experiment_Setup_Instructions.docx` is the original Muse session sheet. Prefer `Muse_Setup.md` for GitHub.

## Repository layout

```
experiments/                 # PsychoPy tasks (need a window and keyboard)
  Level1/                    # Classic Go/No-Go, SART, Semantic
  Level2/                    # Selective visual, Color–number, Spatial cue
  Level3/                    # Picture recall, Color–location, Dual task
  messaging.py               # optional SMS helper
analysis/                    # Jupyter notebooks and session-control scripts
  study1_aps.ipynb           # Study 1 attention scores
  study2_aps.ipynb           # Study 2 attention scores
  behavioral_baps.ipynb      # behavior-only scores when EEG is unusable
  physiology.ipynb           # Study 1 wearable heart rate
  survey.ipynb               # Likert vs behavior
  statistics.ipynb           # Friedman / Wilcoxon
  plot_*.ipynb               # cohort plots
  resting_state.ipynb        # eyes-closed resting EEG
  openbci_qc.ipynb           # OpenBCI file QC
  raw_signal_explorer.ipynb  # leftover voltage, maps, board ECG
  messaging_control_noTwilio.py  # OpenBCI trial markers (send the text from your phone)
Muse_Setup.md
OpenBCI_Setup.md
Experiment_Setup_Instructions.docx
requirements.txt
.env.example
```

PsychoPy stays as `.py`. Jupyter cannot own the task window.

## What is never committed

Recordings, `analysis/outputs/`, Health/XML exports, and office lock files are gitignored on purpose. Clone the repo for code. Copy data through Teams or the lab disk, not through git.

## Ethics

IRB-approved experiments performed to collect human data. Do not put identifiable participant files in this repository.
