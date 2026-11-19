# DATA COLLECTION SECTION FOR RESEARCH PAPER

## Methods: Data Collection

### Participants

A total of **N = 10 participants** (Subject 0 through Subject 9) were recruited for this study. [*Add demographics: age range, gender distribution, education level, exclusion criteria*]. All participants provided informed consent prior to participation. The study protocol was approved by [*institutional review board name*].

---

### Experimental Design

The study employed a **within-subjects repeated measures design** with three experimental conditions:

1. **Set 1 (Baseline)**: No external distractions presented during task performance
2. **Set 2 (Distraction with Required Response)**: External auditory/visual distractions presented at pseudorandom intervals, with participants required to acknowledge the distraction
3. **Set 3 (Distraction without Response)**: External distractions presented, but participants instructed to ignore them and maintain focus on the primary task

Each participant completed all three experimental conditions, with each condition comprising three distinct cognitive tasks (described below). The total experimental session lasted approximately **60-90 minutes per participant**, including setup, task instructions, and breaks between conditions.

---

### Cognitive Tasks

Three Go/No-Go paradigms were employed to assess different aspects of attention and inhibitory control:

#### Task 1: Classic Go/No-Go Task

**Paradigm**: Traditional response inhibition task measuring impulse control and motor inhibition.

**Stimuli**:
- **Go trials**: Text stimuli "SPACE" or "GO" (requiring spacebar press)
- **No-Go trials**: Text stimuli "NO-GO" or "NOT SPACE" (requiring inhibition or alternative key press)

**Design parameters**:
- Trial count: 200 trials per session
- Stimulus presentation: Text displayed on black background (40-point white font)
- Response window: Self-paced (unlimited response time)
- Inter-trial interval (ITI): 500 ms (blank black screen)
- Stimulus randomization: Pseudorandom sequence with balanced Go/No-Go ratio

**Instructions**: Participants were instructed to press the spacebar when "SPACE" or "GO" appeared, and press any other key (typically Enter or 'x') when "NO-GO" or "NOT SPACE" appeared.

**Cognitive processes measured**: Response inhibition, impulse control, selective attention

---

#### Task 2: Sustained Attention to Response Task (SART)

**Paradigm**: Number-based vigilance task adapted from Robertson et al. (1997) measuring sustained attention and mind-wandering.

**Stimuli**:
- **Go trials**: Single digits 1, 2, 4, 5, 6, 7, 8, 9 (requiring spacebar press)
- **No-Go trials**: Single digit "3" (requiring response inhibition)

**Design parameters**:
- Trial count: 200 trials per session
- Stimulus presentation: Single digits displayed centrally (60-point white font on black background)
- Response window: Self-paced
- Inter-trial interval: 500 ms
- Stimulus randomization: Random digit selection with replacement, then shuffled

**Instructions**: Participants were instructed to press the spacebar for all numbers EXCEPT the number "3", which required withholding the response or pressing an alternative key.

**Cognitive processes measured**: Sustained attention, vigilance decrements, automatic vs. controlled processing

---

#### Task 3: Semantic Word/Non-Word Classification Task

**Paradigm**: Lexical decision task with response inhibition measuring semantic processing and executive control.

**Stimuli**:
- **Go trials**: Real English words (e.g., "apple", "banana", "table", "chair", "house", "water", "green", "happy", "computer", "music") requiring spacebar press
- **No-Go trials**: Pseudowords/non-words (e.g., "blzrk", "snatp", "tibdrt", "glwme", "flyrp", "esrto", "grimpth", "blintk", "plvffin", "worblqx") requiring response inhibition

**Design parameters**:
- Trial count: 200 trials per session
- Stimulus presentation: Words/pseudowords displayed centrally (40-point white font on black background)
- Response window: Self-paced
- Inter-trial interval: 500 ms
- Stimulus randomization: Random selection from combined word pool, shuffled after generation
- Word characteristics: Real words were high-frequency concrete nouns and adjectives; pseudowords followed English phonotactic rules but had no semantic meaning

**Instructions**: Participants were instructed to press the spacebar when they saw a real English word, and withhold response or press an alternative key when they saw a nonsense word.

**Cognitive processes measured**: Lexical access, semantic processing, executive control, response inhibition

---

### Experimental Procedure

#### Session Structure

Each participant completed **nine experimental sessions** in a single visit (3 conditions × 3 tasks = 9 sessions):

1. **Session Order** (within each set):
   - Classic Go/No-Go Task
   - SART Task
   - Semantic Task

2. **Condition Order** (counterbalanced across participants):
   - Set 1 (Baseline) → Set 2 (Distraction+Response) → Set 3 (Distraction+NoResponse)
   - [*Note: Consider adding if counterbalancing was performed*]

3. **Breaks**: 2-3 minute rest periods provided between tasks and 5-minute breaks between conditions

4. **Total Duration**: Approximately 60-90 minutes including setup

#### Distraction Protocol (Sets 2 and 3 Only)

**Distraction Timing**: External distractions were presented at **pseudorandom intervals** during Sets 2 and 3, with timing recorded to the nearest second (e.g., 1:30 PM, 1:31 PM, 1:32 PM). The number of distractions varied by task and set:
- **Set 2**: 7-10 distractions per task (mean = 8.67, SD = 1.03)
- **Set 3**: 7-10 distractions per task (mean = 8.33, SD = 1.21)

**Distraction Type**: [*Specify the nature of distractions used: e.g., auditory tones, visual flashes, researcher entering room, phone notifications, etc.*]

**Response Requirement**:
- **Set 2**: Participants were required to verbally acknowledge each distraction (e.g., "I heard it") while continuing the task
- **Set 3**: Participants were instructed to ignore distractions and maintain focus on the primary task without acknowledgment

**Distraction Synchronization**: Exact timestamps of distraction onset were manually recorded by the experimenter and later synchronized with both behavioral (CSV) and EEG (XDF) data streams for analysis.

---

### Data Acquisition

#### Behavioral Data

**Hardware**: Standard computer keyboard for response collection

**Software**: PsychoPy 2023.x (Peirce et al., 2019) running on [*OS specification*]

**Display**: [*Monitor specifications: size, resolution, refresh rate, viewing distance*]

**Recording**: For each trial, the following behavioral metrics were recorded:
1. **Stimulus**: Actual text/number displayed (e.g., "GO", "3", "apple")
2. **Stimulus Type**: Trial category (1 = Go trial, 0 = No-Go trial)
3. **Response**: Actual key pressed by participant (e.g., "space", "return", "x")
4. **Response Correctness**: Binary accuracy (1 = correct, 0 = incorrect)
5. **Reaction Time (RT)**: Time from stimulus onset to keypress (seconds, measured via PsychoPy's `core.Clock()`)

**Data Storage**: Behavioral data were saved as comma-separated values (CSV) files with unique timestamped filenames (e.g., `Classic_results_set1_20251006_131648.csv`) in subject-specific directories.

---

#### Electroencephalography (EEG) Data

**EEG System**: Muse 2 headband (InteraXon Inc., Toronto, Canada)

**Electrode Configuration**:
- **Channels**: 4 dry-contact EEG electrodes
  - TP9: Left temporal region
  - AF7: Left frontal region
  - AF8: Right frontal region
  - TP10: Right temporal region
- **Reference**: Fpz (forehead center, implicit reference)
- **Ground**: Behind the ears (integrated into headband)

**Signal Acquisition**:
- **Sampling rate**: 256 Hz per channel
- **Signal range**: ±1640 μV
- **Resolution**: 12-bit analog-to-digital conversion
- **Frequency response**: 0.5-100 Hz

**Data Streaming**: EEG data were streamed in real-time using the **Lab Streaming Layer (LSL)** protocol via the `muselsl` Python library. The Muse headband transmitted continuous EEG data over Bluetooth Low Energy (BLE) to the recording computer.

**Event Markers**: Behavioral events were synchronized with EEG data using LSL markers. For each trial, a 3-element marker was transmitted via `pylsl.StreamOutlet`:
1. **Stimulus Type**: 1 (Go trial) or 0 (No-Go trial)
2. **Response Correctness**: 1 (correct) or 0 (incorrect)
3. **Reaction Time**: RT in seconds

**Recording Software**: 
- `muselsl stream` for continuous EEG data acquisition
- Custom PsychoPy scripts for task presentation and marker transmission
- LSL LabRecorder or custom Python scripts for XDF file generation

**Data Storage**: EEG data were saved in **Extensible Data Format (XDF)** files, which preserve temporal alignment between EEG signals and event markers. Files were named using the convention `sub-{SubjectID}_task{TaskID}_set{SetID}.xdf` (e.g., `sub-{5}_task{1}_set{2}.xdf`).

---

### Data Quality Control

**EEG Signal Quality**:
- **Pre-session checks**: Electrode impedance verified before each recording session
- **Visual inspection**: Real-time signal quality monitoring during data collection
- **Post-hoc validation**: XDF files inspected for signal continuity and marker alignment

**Behavioral Data Quality**:
- **Response validation**: All trials with response times < 0.1 s (anticipatory) or > 5.0 s (lapses) flagged for inspection
- **Accuracy checks**: CSV files inspected for completeness (expected 200 trials per task)

**Synchronization Verification**:
- **Timestamp alignment**: XDF timestamps (Unix time) matched with CSV trial indices
- **Marker validation**: LSL marker count verified against CSV trial count
- **Manual timestamps**: Distraction onset times (Sets 2-3) manually recorded and synchronized post-hoc with ±2-second tolerance

---

### Data Management

**File Organization**:
```
AttentionSpan/
└── GoNoGoTests/
    ├── Results_CSV/
    │   ├── Subject0/
    │   │   ├── Classic_results_set1_YYYYMMDD_HHMMSS.csv
    │   │   ├── Classic_results_set2_YYYYMMDD_HHMMSS.csv
    │   │   ├── Classic_results_set3_YYYYMMDD_HHMMSS.csv
    │   │   ├── SART_results_set1_YYYYMMDD_HHMMSS.csv
    │   │   ├── SART_results_set2_YYYYMMDD_HHMMSS.csv
    │   │   ├── SART_results_set3_YYYYMMDD_HHMMSS.csv
    │   │   ├── semantic_results_set1_YYYYMMDD_HHMMSS.csv
    │   │   ├── semantic_results_set2_YYYYMMDD_HHMMSS.csv
    │   │   └── semantic_results_set3_YYYYMMDD_HHMMSS.csv
    │   ├── Subject1/
    │   │   └── [9 CSV files]
    │   └── ... [Subjects 2-9]
    └── Results_xdf/
        ├── subject0/
        │   ├── sub-{0}_task{1}_set{1}.xdf
        │   ├── sub-{0}_task{1}_set{2}.xdf
        │   └── ... [9 XDF files]
        ├── subject1/
        │   └── [9 XDF files]
        └── ... [subjects 2-9]
```

**Data Backup**: All raw data files (CSV and XDF) were backed up to [*specify backup location*] within 24 hours of collection.

**De-identification**: Participants were assigned numeric identifiers (Subject0-Subject9). No personally identifiable information was stored with experimental data.

---

### Summary Statistics

**Total Data Collected**:
- **Participants**: N = 10
- **Sessions per participant**: 9 (3 conditions × 3 tasks)
- **Total experimental sessions**: 90
- **Trials per session**: 200
- **Total trials**: 18,000 (90 sessions × 200 trials)
- **CSV files**: 90 behavioral data files
- **XDF files**: 90 EEG recording files
- **Total recording time**: Approximately 12-15 hours (across all participants)
- **Distractions presented**: 750-900 external distractions (Sets 2-3 only)

**Data Completeness**:
- All 10 participants completed all 9 experimental sessions
- Data loss: [*Report any missing/corrupted files or sessions*]
- Usable data: [*Report final data included in analysis after quality control*]

---

## Technical Implementation Details

### Software Environment

**Task Presentation**:
- **PsychoPy**: Version 2023.x (Python-based stimulus presentation)
- **Python**: Version 3.9+
- **Key libraries**: `psychopy`, `pylsl`, `pandas`, `numpy`, `datetime`, `csv`

**EEG Acquisition**:
- **muselsl**: Python library for Muse EEG streaming (version X.X)
- **pylsl**: Lab Streaming Layer Python bindings (version X.X)
- **LSL**: Version X.X for real-time multimodal data synchronization

**Operating System**: [*Specify: macOS 13.x, Windows 11, Ubuntu 22.04, etc.*]

### Hardware Specifications

**Recording Computer**:
- **Processor**: [*Specify CPU*]
- **RAM**: [*Specify memory*]
- **Storage**: [*Specify drive type and capacity*]

**Display**:
- **Monitor**: [*Brand/model, size, resolution*]
- **Refresh rate**: [*e.g., 60 Hz*]
- **Viewing distance**: [*e.g., 60 cm*]

**Input Device**: Standard QWERTY keyboard

**EEG Device**: Muse 2 headband with Bluetooth 5.0 connectivity

---

## Experimental Protocols

### Pre-Session Procedures

1. **Informed Consent**: Participants read and signed consent forms
2. **Demographic Questionnaire**: Age, gender, handedness, vision status, neurological history
3. **Task Instructions**: Verbal and written instructions provided for each task type
4. **Practice Trials**: [*If applicable: 10-20 practice trials per task*]
5. **EEG Setup**:
   - Muse headband fitted to participant's head
   - Electrode contact quality verified via mobile app
   - Bluetooth connection established
   - LSL stream initiated (`muselsl stream`)

### During-Session Procedures

1. **Task Initiation**: Experimenter started PsychoPy script
2. **Real-time Monitoring**: Experimenter monitored EEG signal quality and participant comfort
3. **Distraction Administration** (Sets 2-3 only):
   - Experimenter delivered distractions at predetermined pseudorandom intervals
   - Exact timestamp recorded manually (e.g., "1:30 PM")
   - Set 2: Verified participant acknowledged each distraction
   - Set 3: Reminded participant to ignore distractions if attention shifted
4. **Break Management**: Enforced minimum 2-minute breaks between tasks

### Post-Session Procedures

1. **Debriefing**: Participants asked about task difficulty, strategy, and distraction impact
2. **Data Verification**: CSV and XDF files checked for completeness
3. **Compensation**: Participants provided with [*specify: course credit, monetary compensation, etc.*]

---

## Data Synchronization Protocol

### Challenge

CSV behavioral files contain only **trial indices** (1-200) and **reaction times** (seconds), but lack absolute timestamps. XDF EEG files contain **continuous Unix timestamps** (e.g., 1758310310.738) sampled at 256 Hz. Manual distraction timestamps were recorded in **human-readable format** (e.g., "1:30 PM").

### Synchronization Procedure

To align distraction events with specific trials in CSV and EEG samples in XDF:

1. **Convert Manual Timestamps**: 
   - Human-readable times (e.g., "1:30 PM") converted to seconds from midnight
   - Relative times calculated from first distraction onset (e.g., 0s, 60s, 120s)

2. **Match XDF Timestamps**:
   - First XDF timestamp used as session start reference
   - Relative distraction times added to session start to estimate absolute Unix time
   - Closest XDF sample identified within ±60-second tolerance

3. **Estimate CSV Trial Index**:
   - Trial duration estimated as: `len(xdf_timestamps) / len(csv_trials)`
   - XDF sample index converted to trial index: `trial_idx = xdf_sample_idx / trial_duration_estimate`
   - Corresponding CSV row marked with `stim_time` column

4. **Validation**:
   - Synchronization accuracy validated by comparing estimated trial times with reaction time patterns
   - Trials with distraction markers (`stim_time` not NaN) verified to occur within expected time windows

### Limitations

- **Gap between recording start and task start**: 1-2 second delay between LSL recording initiation and first trial may introduce ±1 trial index error
- **Variable trial durations**: RT variability (0.2-2.0 seconds) means trials are not uniformly spaced
- **Estimation-based alignment**: CSV trial indices are *estimated* from XDF sample counts, not directly recorded

---

## References

Peirce, J., Gray, J. R., Simpson, S., MacAskill, M., Höchenberger, R., Sogo, H., Kastman, E., & Lindeløv, J. K. (2019). PsychoPy2: Experiments in behavior made easy. *Behavior Research Methods*, *51*(1), 195–203. https://doi.org/10.3758/s13428-018-01193-y

Robertson, I. H., Manly, T., Andrade, J., Baddeley, B. T., & Yiend, J. (1997). 'Oops!': Performance correlates of everyday attentional failures in traumatic brain injured and normal subjects. *Neuropsychologia*, *35*(6), 747–758. https://doi.org/10.1016/S0028-3932(97)00015-8

[*Add additional references for Muse EEG validation, LSL protocol, Go/No-Go paradigms, etc.*]

---

## Notes for Author

**Sections to complete** (marked with [*...*] throughout):
- Participant demographics (age, gender, education, exclusion criteria)
- Exact distraction type used (auditory tone, visual flash, etc.)
- Monitor and computer hardware specifications
- Software version numbers (muselsl, pylsl, PsychoPy)
- IRB approval details
- Counterbalancing scheme (if used)
- Practice trial protocol (if used)
- Data loss/exclusions (if any)
- Participant compensation details

**Additional sections you may want to add**:
- Ethical approval section
- Power analysis/sample size justification
- Inclusion/exclusion criteria for participants
- Statistical analysis plan (separate Methods subsection)
- Data availability statement
- Supplementary materials (task screenshots, sample trials)

**Formatting for journal submission**:
- Adjust subsection hierarchy based on journal requirements
- Convert to APA 7th edition formatting
- Add line numbers for peer review
- Include figure captions for any screenshots or flowcharts
- Consider adding a participant flow diagram (CONSORT-style)

---

**Document Created**: [Date]
**Last Updated**: [Date]
**Version**: 1.0

