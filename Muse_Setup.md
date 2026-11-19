# Muse setup (Study 1)

Step-by-step for running a PsychoPy task while streaming Muse 2 EEG over LSL and saving one `.xdf` plus a behavioral CSV. This is the Study 1 collection path. For 16-channel board recordings see [OpenBCI_Setup.md](OpenBCI_Setup.md).

## What you will run

Three terminals:

1. **EEG stream** — Muse LSL
2. **Task** — PsychoPy script (markers + behavior)
3. **Recorder** — writes all LSL streams to one `.xdf`

You also get a CSV with trial-level behavior.

## Hardware

- Charge the Muse 2. Sites are TP9, AF7, AF8, TP10.
- Bluetooth on the Mac. **Do not pair** the headband in macOS Settings; `muselsl` talks BLE itself.
- Seat the band centered, with contact. Close the Muse phone app so it does not steal the connection.
- Keyboard and display for the task. Optional Hume band for heart rate (start it before Level 2 if you use it; Level 1 often missed the start-up window).

## One-time software (this Mac)

```bash
conda create -n attn python=3.9 -y
conda activate attn
conda install -c conda-forge liblsl -y
pip install "numpy==1.25.2" "scipy>=1.9,<1.12" psychopy==2022.2.5 \
  muselsl==2.3.1 pylsl==1.17.6 pyxdf==1.17.0 bitstring==4.2.3
```

Apple Silicon: if you hit a `liblsl` / DYLD error:

```bash
export DYLD_LIBRARY_PATH="$CONDA_PREFIX/lib"
```

Add that line to `~/.zshrc` so it sticks.

Check you are inside the env:

```bash
conda activate attn
which python
python -c "import numpy, scipy, psychopy, muselsl, pylsl, pyxdf; print('ok')"
which muselsl
```

If `which muselsl` is outside the env, call `python -m muselsl` instead.

From the repo you can also `pip install -r requirements.txt` for the shared analysis packages. Prefer `python -m pip` so the install lands in `attn`.

Twilio SMS is optional. Copy `.env.example` to `.env` and fill it. Never commit `.env`.

## Every session

### 1. Activate

```bash
conda activate attn
cd /path/to/AttentionSpan
```

Prompt must show `(attn)`.

### 2. Power on Muse and start the stream (terminal 1)

```bash
python -m muselsl list      # optional: see the headband
python -m muselsl stream    # leave this running
```

You want `Connected. Streaming EEG....`

### 3. Open the task (terminal 2)

In each task script set `SUBJECT_ID` and `SET_ID`:

| Set | Condition |
|-----|-----------|
| 1 | Baseline (no phone) |
| 2 | Text + reply |
| 3 | Text + glance only |

```bash
cd experiments/Level1
python SART_task2.py
```

Wait for the READY screen. The Markers stream is live now. Do not start trials yet.

Other tasks live under `experiments/Level2/` and `experiments/Level3/`.

### 4. Start the recorder (terminal 3)

Start **after** READY so the recorder sees Markers:

```bash
mkdir -p experiments/Level1/Results_xdf
cd experiments/Level1/Results_xdf
python -m muselsl record -f sub-XXX_set-N_task-sart.xdf
```

Use a unique name per person and task (`sub-007_set-2_task-sart.xdf`).

### 5. Run trials

Back in the PsychoPy window, press Enter. Run the block.

### 6. Stop

- Task saves CSV under `experiments/LevelN/Results_CSV/Subject{ID}/` (gitignored).
- Ctrl+C the recorder (XDF is written).
- Ctrl+C the Muse stream.

## Check the XDF (optional)

```python
import pyxdf
streams, header = pyxdf.load_xdf("experiments/Level1/Results_xdf/sub-XXX_set-N_task-sart.xdf")
for s in streams:
    name = s["info"]["name"][0]
    stype = s["info"]["type"][0]
    print(f"{name:15s}  {stype:8s}  n={len(s['time_series'])}")
```

You should see EEG and Markers.

## Marker meaning (Muse / LSL)

The Markers stream is `[trial_id, code]` per sample.

- Stimulus: `1` word / go, `0` non-word / no-go (task-dependent).
- Response: `101` right, `100` left, `0` no response (task-dependent).

Join to the behavioral CSV on `trial_id`.

## After the sitting — analysis

From the **repo root**, `attn` kernel:

```bash
jupyter notebook analysis/study1_aps.ipynb
```

Run cells in order. The last cell is the interactive scorer (level, subject, ping times).

```bash
export ATTENTIONSPAN_DATA=/path/to/folder     # must contain Level1/, Level2/, Level3/
export ATTENTIONSPAN_OUTPUT=/path/to/out      # default: analysis/outputs
```

Related notebooks: `behavioral_baps.ipynb`, `physiology.ipynb` (Hume / Apple Health), `survey.ipynb`, `statistics.ipynb`, `plot_*.ipynb`, `resting_state.ipynb`.

Hume HR: use Levels 2–3. FAA is not scored.

## If something breaks

| Problem | What to try |
|---------|-------------|
| No Markers stream | Start `record` **after** the task READY screen |
| Wrong Python | Prompt must be `(attn)`. `which python`; `which muselsl` |
| DYLD / liblsl | `export DYLD_LIBRARY_PATH="$CONDA_PREFIX/lib"` |
| PsychoPy / NumPy import | Reinstall the pinned versions in the block above |
| Stream dropped | Headband ≤2–3 m, charged, Muse app closed, less 2.4 GHz clutter |
| Empty EEG in the XDF | Terminal 1 must stay in `muselsl stream` the whole sitting |

## Quick reset

1. `conda activate attn`
2. `python -m muselsl stream`
3. `python experiments/Level1/SART_task2.py` → READY
4. `python -m muselsl record -f …/sub-XXX_set-N_task-….xdf`
5. Enter to start trials
6. End → CSV in `Results_CSV/`, XDF in `Results_xdf/`

Do not commit those folders. Copy them to Teams if that is the lab backup.
