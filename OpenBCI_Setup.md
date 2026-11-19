# OpenBCI setup (Study 2)

Tutorial for recording 16-channel EEG (and optional ECG) on the Cyton+Daisy while someone does the AttentionSpan tasks, then opening those files in the explorer notebook. For the Muse / LSL path see [Muse_Setup.md](Muse_Setup.md).

## What this sitting produces

- One BrainFlow CSV per recording from the OpenBCI GUI (125 Hz, 16 EXG channels + marker column)
- Event stamps in that same file: set id `101`–`104`, then `1` / `11` / `12` on each trial
- After analysis: leftover plots and optional heart-rate plots under `analysis/outputs/raw_signals/<subject>/` (gitignored)

PsychoPy still runs the cognitive tasks. The board recording is separate from the Study 1 `.xdf` files.

## Hardware

- OpenBCI **Cyton + Daisy**, 16 channels, default 125 Hz, ±187500 µV
- Dry EEG cap wired to the default GUI 10–20 map (change the table in `analysis/openbci_qc.py` if you wired differently):

| Board | 10–20 |
|-------|-------|
| N1P Ch0 | Fp1 |
| N2P Ch1 | Fp2 |
| N3P Ch2 | C3 |
| N4P Ch3 | C4 |
| N5P Ch4 | P7 |
| N6P Ch5 | P8 |
| N7P Ch6 | O1 |
| N8P Ch7 | O2 |
| N1P' Ch8 | F7 |
| N2P' Ch9 | F8 |
| N3P' Ch10 | F3 |
| N4P' Ch11 | F4 |
| N5P' Ch12 | T7 |
| N6P' Ch13 | T8 |
| N7P' Ch14 | P3 |
| N8P' Ch15 | P4 |

- USB dongle, charged board, good skin contact. Let the stream settle ~45 s before you care about the trace.
- Optional **ECG snaps on N1P (Ch0)** with **SRB2 off** for that channel: bottom pin under the **left** collarbone, upper pin under the **right**. Other channels stay EEG. The GUI still labels Ch0 as Fp1 — that is only the pin name.

## Software on this Mac

Two conda envs:

| Env | Use |
|-----|-----|
| `attn` | PsychoPy tasks |
| `attn_analysis` | Jupyter plots (`attn` cannot rasterize PNG) |

OpenBCI GUI: [openbci.com](https://openbci.com). Recordings default to:

```
~/Documents/OpenBCI_GUI/Recordings/
```

Session-control scripts (from repo root, `attn_analysis` or `attn`):

```bash
conda activate attn_analysis
cd /path/to/AttentionSpan
python analysis/messaging_control_noTwilio.py
```

This script only stamps the EEG file. Send the text from your own phone. Optional SMS helper: `experiments/messaging.py` (uses `.env`, not the board).

## GUI before you hit Record

1. Cyton + Daisy, 16 channels, live time series looks like EEG (not rails).
2. Add the **Marker** widget (not Networking).
3. Marker **Receive IP** `127.0.0.1`, **Receive Port** `12350`.
4. If Ch0 is ECG: hardware settings → **SRB2 off** on that channel.
5. Start **Record**. Wait for the CSV to appear. Then start the marker script. The console should say `Inserted marker 1.0` when you stamp.

## Markers

At the start of a run the control script stamps the set:

| Stamp | Meaning |
|-------|---------|
| 101 | set 1 baseline |
| 102 | set 2 text + reply |
| 103 | set 3 text + glance |
| 104 | set 4 auditory ping |

Then, on every trial:

| Stamp | Key | Meaning |
|-------|-----|---------|
| 1 | `S` (with Send / ping) | notification onset |
| 11 | Space | they engaged (pickup or glance) |
| 12 | Space again | phone down / eyes back |

**Set 4:** eyes stay on the task. Press `S` with the ping. Do **not** press Space unless they look at the phone anyway. Analysis then sees `1` only.

Press `S` and Send (or the ping) **together**. Pre-type the message; thumb on Send, other hand on `S`.

## Run-day order

1. Cap / snaps on. GUI streaming. Impedance / time series acceptable.
2. Start **Record** in the GUI.
3. `conda activate attn_analysis` (or `attn` for PsychoPy).
4. `python analysis/messaging_control_noTwilio.py` — pick the set; it stamps `101`–`104`.
5. Start the PsychoPy task if this sitting includes one (`experiments/LevelN/…`, `SUBJECT_ID` / `SET_ID` filled in).
6. For each distraction: `S`+Send → Space on engage → Space on release.
7. Stop the control script with `Q`. Stop GUI Record.
8. Name the sitting in the handwritten notebook (person, set, date, SRB2, anything odd).

CSV names look like `BrainFlow-RAW_2026-11-16_15-19-56-PriyaSet2_0.csv`. Leave them in the GUI Recordings folder until you import them in the notebook (the notebook copies them into a subject folder).

## After the sitting — explorer notebook

Kernel: **`attn_analysis`**. From the repo root:

```bash
conda activate attn_analysis
jupyter notebook analysis/raw_signal_explorer.ipynb
```

Run **in order**:

1. **Select** — pick or create a subject folder (`Priya`, `Soni`, …). Tag set 1 / 2 / 3 / 4 and Command-click those CSVs. Files are copied to `analysis/outputs/raw_signals/<subject>/setN/recordings/` (not git).
2. **Load** — `LOAD_SET = 2` (only that set, so QC does not load every CSV).
3. **Pack** — `WORK_ON = "pooled"` or `0` / `1` for one sitting. `VIEW_CH = "P3"` (a scalp site, not Fp1 when Ch0 is ECG).
4. **Cleanup ladder** — high-pass, notch, low-pass, CAR. ICA only after you look at Cell D. Blink-like: high kurtosis **and** high frontal weight. Fill `ICA_DROP` in Cell E (often `[0]`).
5. **Meeting plots** — leftover clip. Tune `SAW_*` on **this** clip; voltages are not the same every sitting.
6. **Scalp maps** — optional.
7. **ECG / heart rate** — last two cells. Uses N1P/Ch0 only. Does not run the EEG 3–80 µV RMS gate on Ch0.

Also useful: `analysis/openbci_qc.ipynb` (file-level QC tables) and `analysis/openbci_patterns.ipynb`.

Plots (leftover and heart-rate `ecg_*.png`) go to `analysis/outputs/raw_signals/<subject>/setN/<channel>/`. Heart rate is section 7 of `raw_signal_explorer.ipynb`, not a separate folder. Never commit that tree.

## Optional ECG notes

- Ch0 millivolt-scale is expected. Do not drop it for “railed EEG” in the ECG cells.
- Leftover `VIEW_CH` should stay on C3 / P3 / … so ECG does not masquerade as a scalp leftover.
- Heart rate is from R–R on the board. That is not the Study 1 Hume / Apple Health number. A 5 bpm change is only a descriptive flag, same cut as Study 1.

## If something breaks

| Problem | What to try |
|---------|-------------|
| No markers in the CSV | Marker widget, port **12350**, Record **before** the Python script |
| `Device not configured` / plots fail | Switch Jupyter kernel to **attn_analysis** |
| Timeout loading CSVs | Set `LOAD_SET` to one set; do not QC every set at once |
| Two sittings of the same set mixed | `WORK_ON = 0` or `1`, not `"pooled"` |
| ICA table, frontal-weight 0.00 | No frontal channels in the USABLE set; judge from the IC traces |
| Explorer tab looks old | Reload / Revert the `.ipynb`; ECG is the **last** section |
| Huge notebook / slow GitHub | Do not save plot outputs in the `.ipynb` |

## Quick reset

1. GUI streaming + Marker widget `127.0.0.1:12350` → Record
2. `python analysis/messaging_control_noTwilio.py` → set stamp
3. Task if needed; `S` / Space per trial (set 4: `S` only)
4. Stop Record
5. `raw_signal_explorer.ipynb` → subject folder → `LOAD_SET` → pack → leftover → ECG
