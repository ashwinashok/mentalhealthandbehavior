# DATA ANALYSIS SECTION FOR RESEARCH PAPER

## Methods: Data Analysis

### Overview

All data analysis was performed using custom Python scripts (`unified_eeg_analysis.py`) built on the scientific computing stack (NumPy 1.x, Pandas 2.x, SciPy 1.x, scikit-learn 1.x, Matplotlib 3.x). The analysis pipeline consisted of four major stages: (1) EEG preprocessing, (2) frequency band extraction, (3) attention metric calculation, and (4) composite attention span scoring. All code is available at [*GitHub repository URL*].

---

## Stage 1: EEG Preprocessing

EEG signals from the Muse headband (4 channels: TP9, AF7, AF8, TP10; 256 Hz sampling rate) underwent preprocessing to remove artifacts and isolate neural signals of interest. Two preprocessing pipelines were implemented:

### 1.1 Basic Preprocessing Pipeline

**Purpose**: Fast, stable preprocessing suitable for real-time applications and exploratory analysis.

**Steps**:

#### 1.1.1 Artifact Removal by Amplitude Thresholding

**Implementation** (Lines 179-187):
```python
for channel in ['TP9', 'AF7', 'AF8', 'TP10']:
    eeg_data.loc[eeg_data[channel] > 500, channel] = NaN
    eeg_data.loc[eeg_data[channel] < -500, channel] = NaN
    eeg_data[channel] = eeg_data[channel].interpolate()
```

**Rationale**: Muse headband dry electrodes are susceptible to movement artifacts and poor contact, producing extreme amplitude values (>500 μV or <-500 μV). These values are physiologically implausible for EEG (typical EEG: 10-100 μV) and indicate recording artifacts rather than neural activity.

**Method**: Any sample exceeding ±500 μV was replaced with NaN and linearly interpolated from surrounding values using pandas' `.interpolate()` method.

**Justification**: Linear interpolation preserves temporal continuity while removing gross artifacts. This threshold is conservative—normal EEG rarely exceeds ±200 μV (Luck, 2014).

#### 1.1.2 Bandpass Filtering (1-44 Hz)

**Implementation** (Lines 189-198):
```python
nyquist = 256 / 2  # 128 Hz
low_cutoff = 1.0 / nyquist   # 0.0078 normalized frequency
high_cutoff = 44.0 / nyquist # 0.34375 normalized frequency

b, a = signal.butter(4, [low_cutoff, high_cutoff], btype='band')
eeg_data[channel] = signal.filtfilt(b, a, eeg_data[channel])
```

**Rationale**: 
- **High-pass (1 Hz)**: Removes slow drifts, DC offsets, and skin potential artifacts
- **Low-pass (44 Hz)**: Removes high-frequency noise while preserving gamma band activity (30-44 Hz)
- **Filter type**: 4th-order Butterworth filter provides maximally flat passband response
- **Zero-phase filtering**: `filtfilt()` applies the filter forward and backward, eliminating phase distortion

**Justification**: This frequency range captures all canonical EEG bands (delta, theta, alpha, beta, gamma) while excluding low-frequency drift (<1 Hz) and high-frequency muscle artifacts (>44 Hz) (Widmann et al., 2015).

**Mathematical formulation**:
The Butterworth filter transfer function:

$$H(j\omega) = \frac{1}{\sqrt{1 + (\omega/\omega_c)^{2n}}}$$

Where:
- $\omega$ = angular frequency
- $\omega_c$ = cutoff frequency
- $n$ = filter order (4 in this implementation)

---

### 1.2 Advanced Preprocessing Pipeline

**Purpose**: Research-grade preprocessing with sophisticated artifact removal for publication-quality analysis.

**Steps**:

#### 1.2.1 Initial Artifact Removal (Lines 215-223)

**Threshold**: ±100 μV (more stringent than basic preprocessing)

**Rationale**: Advanced preprocessing uses a lower threshold to catch subtler artifacts before applying ICA, which is sensitive to extreme values.

#### 1.2.2 Notch Filtering at 60 Hz (Lines 225-235)

**Implementation**:
```python
freq = 60 / (256/2)  # Normalized frequency
b, a = signal.iirnotch(freq, Q=30)
eeg_data[channel] = signal.filtfilt(b, a, eeg_data[channel])
```

**Rationale**: Removes power line interference from 60 Hz AC electrical systems (50 Hz in some countries). The Q-factor of 30 creates a narrow notch (±2 Hz bandwidth) that removes line noise without affecting nearby frequencies.

**Mathematical formulation**:
Notch filter transfer function:

$$H(z) = \frac{b_0 + b_1z^{-1} + b_2z^{-2}}{1 + a_1z^{-1} + a_2z^{-2}}$$

Where coefficients are calculated to create a zero at 60 Hz with specified Q-factor.

#### 1.2.3 Bandpass Filtering (Lines 237-246)

**Identical to basic preprocessing** (1-44 Hz, 4th-order Butterworth, zero-phase).

#### 1.2.4 Re-referencing (Lines 249-257)

**Implementation**:
```python
avg_ref = eeg_data[['TP9', 'AF7', 'AF8', 'TP10']].mean(axis=1)
for channel in ['TP9', 'AF7', 'AF8', 'TP10']:
    eeg_data[channel] = eeg_data[channel] - avg_ref
```

**Rationale**: 
- Muse headband uses Fpz (forehead center) as the reference electrode
- Average referencing transforms data to a reference-free space
- Each channel is re-referenced to the average of all channels
- This reduces common-mode noise and makes signals comparable across channels

**Mathematical formulation**:

$$V_{ch,avg} = V_{ch,Fpz} - \frac{1}{N}\sum_{i=1}^{N} V_{i,Fpz}$$

Where:
- $V_{ch,avg}$ = channel voltage after average referencing
- $V_{ch,Fpz}$ = original voltage referenced to Fpz
- $N$ = number of channels (4)

**Justification**: Average referencing is standard practice in EEG analysis (Luck, 2014; Nunez & Srinivasan, 2006) and reduces reference-dependent biases.

#### 1.2.5 Independent Component Analysis (ICA) for Artifact Removal (Lines 259-323)

**Implementation**:
```python
from sklearn.decomposition import FastICA

# Robust NaN/Inf handling (lines 263-290)
eeg_data[channel] = eeg_data[channel].replace([np.inf, -np.inf], np.nan)
eeg_data[channel] = eeg_data[channel].interpolate(method='linear')
eeg_data[channel] = eeg_data[channel].fillna(method='ffill').fillna(method='bfill')

# ICA decomposition
eeg_matrix = eeg_data[['TP9', 'AF7', 'AF8', 'TP10']].values.T
ica = FastICA(n_components=4, random_state=42, max_iter=1000)
sources = ica.fit_transform(eeg_matrix.T).T

# Artifact detection
stds = [np.std(source) for source in sources]
median_std = np.median(stds)
artifact_components = [i for i, std in enumerate(stds) if std > 3 * median_std]

# Artifact removal
sources_clean = sources.copy()
sources_clean[artifact_components, :] = 0
eeg_clean = ica.inverse_transform(sources_clean.T).T
```

**Rationale**:
- **ICA assumption**: EEG signals are mixtures of independent neural and artifact sources
- **Blind source separation**: ICA unmixes these sources without prior knowledge
- **Artifact identification**: Components with variance >3× median are likely artifacts (eye blinks, muscle activity, electrode movement)
- **Selective removal**: Only artifact components are zeroed; neural components are preserved

**Mathematical formulation**:

ICA assumes the observed EEG signals $\mathbf{X}$ are linear mixtures of independent sources $\mathbf{S}$:

$$\mathbf{X} = \mathbf{A}\mathbf{S}$$

Where:
- $\mathbf{X}$ = observed EEG (4 channels × T samples)
- $\mathbf{S}$ = independent source signals (4 sources × T samples)
- $\mathbf{A}$ = mixing matrix (4 × 4)

ICA finds the unmixing matrix $\mathbf{W}$ such that:

$$\mathbf{S} = \mathbf{W}\mathbf{X}$$

FastICA maximizes non-Gaussianity of sources using negentropy approximation:

$$J(s) \approx [E\{G(s)\} - E\{G(\nu)\}]^2$$

Where $G$ is a non-quadratic function (typically $G(u) = \log \cosh(u)$) and $\nu \sim \mathcal{N}(0,1)$.

After identifying artifacts (sources with $\sigma_i > 3 \times \text{median}(\sigma)$), clean EEG is reconstructed:

$$\mathbf{X}_{clean} = \mathbf{A}\mathbf{S}_{clean}$$

Where $\mathbf{S}_{clean}$ has artifact components set to zero.

**Justification**: ICA is the gold standard for removing ocular and muscle artifacts from EEG (Jung et al., 2000; Makeig et al., 1996). The variance-based criterion effectively identifies non-neural components (Delorme et al., 2007).

#### 1.2.6 Statistical Outlier Removal (Lines 325-335)

**Implementation**:
```python
from scipy.stats import zscore

z_scores = np.abs(zscore(eeg_data[channel]))
outlier_mask = z_scores > 4
eeg_data.loc[outlier_mask, channel] = NaN
eeg_data[channel] = eeg_data[channel].interpolate(method='linear')
```

**Rationale**: 
- Even after ICA, isolated extreme values may remain
- Z-score identifies samples >4 standard deviations from the mean
- Z > 4 captures only ~0.006% of normally distributed data (extreme outliers)

**Mathematical formulation**:

$$z_i = \frac{x_i - \bar{x}}{\sigma_x}$$

Where:
- $x_i$ = EEG sample at time $i$
- $\bar{x}$ = channel mean
- $\sigma_x$ = channel standard deviation

Outliers defined as $|z_i| > 4$.

**Justification**: Conservative threshold (Z > 4) minimizes false positives while removing genuine artifacts. This is more stringent than typical psychological cutoffs (Z > 3) due to EEG's non-normal amplitude distribution.

---

## Stage 2: Frequency Band Extraction

### 2.1 Frequency Band Definitions (Lines 64-71)

Standard EEG frequency bands based on Muse documentation and neurophysiological literature:

| Band | Frequency Range | Associated Cognitive Processes |
|------|----------------|-------------------------------|
| **Delta (δ)** | 1-4 Hz | Deep sleep, unconscious processes |
| **Theta (θ)** | 4-8 Hz | Drowsiness, meditation, working memory |
| **Alpha (α)** | 7.5-13 Hz | Relaxed wakefulness, idling, inhibition |
| **Beta (β)** | 13-30 Hz | Active thinking, focus, alertness |
| **Gamma (γ)** | 30-44 Hz | Higher-order cognition, binding |

**Note**: Alpha and theta bands overlap (7.5-8 Hz) to capture transitional activity.

### 2.2 Band Power Extraction (Lines 370-394)

**Implementation**:
```python
for band_name, (low_freq, high_freq) in freq_bands.items():
    # Design bandpass filter for specific band
    nyquist = 256 / 2
    low = low_freq / nyquist
    high = high_freq / nyquist
    
    b, a = signal.butter(4, [low, high], btype='band')
    filtered = signal.filtfilt(b, a, eeg_data[channel])
    
    # Calculate power (RMS)
    power = np.sqrt(np.mean(filtered**2))
    band_powers[band_name][channel] = power
```

**Rationale**:
1. **Bandpass filtering**: Isolates activity in each frequency band
2. **RMS power calculation**: Root-mean-square provides amplitude-independent power estimate
3. **Per-channel computation**: Preserves spatial information (frontal vs. temporal activity)

**Mathematical formulation**:

For each frequency band $f_b$ with range $[f_{low}, f_{high}]$:

$$P_{ch,f_b} = \sqrt{\frac{1}{T}\sum_{t=1}^{T} [x_{ch,f_b}(t)]^2}$$

Where:
- $P_{ch,f_b}$ = power in band $f_b$ for channel $ch$
- $x_{ch,f_b}(t)$ = filtered signal in band $f_b$ at time $t$
- $T$ = total number of samples

**Alternative formulations** (not implemented, but common):
- **Welch's method**: Periodogram averaging for spectral density
- **Wavelet transform**: Time-frequency decomposition

**Justification**: RMS power is computationally efficient, robust to amplitude scaling, and directly interpretable as signal strength. Filtering in the time domain (rather than FFT) preserves temporal resolution for subsequent trial-based analysis.

---

## Stage 3: Attention Metrics Calculation

### 3.1 Alpha/Beta Ratio (Lines 764-772)

**Implementation**:
```python
alpha_beta_ratio[channel] = alpha_power[channel] / (beta_power[channel] + 1e-10)
```

**Rationale**:
- **High alpha/low beta**: Relaxed, internally-focused state
- **Low alpha/high beta**: Externally-focused attention, active processing
- **Clinical relevance**: Used in neurofeedback for attention training

**Mathematical formulation**:

$$R_{\alpha/\beta,ch} = \frac{P_{\alpha,ch}}{P_{\beta,ch} + \epsilon}$$

Where:
- $R_{\alpha/\beta,ch}$ = alpha/beta ratio for channel $ch$
- $P_{\alpha,ch}$ = alpha band power (7.5-13 Hz)
- $P_{\beta,ch}$ = beta band power (13-30 Hz)
- $\epsilon = 10^{-10}$ = small constant to prevent division by zero

**Interpretation**:
- $R_{\alpha/\beta} < 0.5$: High focused attention, active engagement
- $R_{\alpha/\beta} \approx 0.5-1.0$: Moderate attention, balanced processing
- $R_{\alpha/\beta} > 1.0$: Relaxed state, internal focus, disengagement

**Justification**: Alpha desynchronization (decreased alpha power) during attention tasks is well-established (Klimesch, 2012; Pfurtscheller & Lopes da Silva, 1999). Beta power increases during cognitive effort (Engel & Fries, 2010).

### 3.2 Theta/Beta Ratio (Lines 774-782)

**Implementation**:
```python
theta_beta_ratio[channel] = theta_power[channel] / (beta_power[channel] + 1e-10)
```

**Rationale**:
- **Clinical relevance**: Elevated theta/beta ratio is a biomarker for ADHD (Snyder & Hall, 2006)
- **Cognitive interpretation**: High theta/beta indicates mind-wandering, reduced attention
- **Neurofeedback target**: ADHD interventions aim to reduce theta/beta ratio

**Mathematical formulation**:

$$R_{\theta/\beta,ch} = \frac{P_{\theta,ch}}{P_{\beta,ch} + \epsilon}$$

Where:
- $R_{\theta/\beta,ch}$ = theta/beta ratio for channel $ch$
- $P_{\theta,ch}$ = theta band power (4-8 Hz)
- $P_{\beta,ch}$ = beta band power (13-30 Hz)

**Interpretation**:
- $R_{\theta/\beta} < 0.5$: High alertness, sustained attention
- $R_{\theta/\beta} \approx 0.5-1.0$: Normal attention variability
- $R_{\theta/\beta} > 1.0$: Increased distractibility, mind-wandering

**Justification**: Theta increases during mental fatigue and lapses of attention (Borghini et al., 2014). The theta/beta ratio has 80-90% sensitivity for ADHD diagnosis (Monastra et al., 2001).

### 3.3 Frontal Alpha Asymmetry (Lines 784-788)

**Implementation**:
```python
frontal_asymmetry = alpha_power['AF8'] - alpha_power['AF7']
```

**Rationale**:
- **Lateralization theory**: Left frontal (AF7) associated with approach motivation; right frontal (AF8) with withdrawal
- **Sign convention**: Positive asymmetry = right-hemisphere dominance; negative = left-hemisphere dominance
- **Emotional valence**: Related to approach/avoidance behaviors

**Mathematical formulation**:

$$A_{frontal} = P_{\alpha,AF8} - P_{\alpha,AF7}$$

Where:
- $A_{frontal}$ = frontal alpha asymmetry
- $P_{\alpha,AF8}$ = right frontal alpha power
- $P_{\alpha,AF7}$ = left frontal alpha power

**Alternative formulation** (ln-transformed, more common in literature):

$$A_{frontal} = \ln(P_{\alpha,AF8}) - \ln(P_{\alpha,AF7})$$

**Interpretation**:
- $A_{frontal} > 0.1$: Right-hemisphere dominant (withdrawal, negative affect)
- $A_{frontal} \approx -0.1 \text{ to } 0.1$: Balanced hemispheric activity
- $A_{frontal} < -0.1$: Left-hemisphere dominant (approach, positive affect)

**Justification**: Frontal alpha asymmetry is robustly associated with emotional processing and motivation (Davidson, 2004; Harmon-Jones et al., 2010). In attention tasks, left frontal activation (reduced left alpha) indicates engagement.

---

### 3.4 EEG Recovery Time (Lines 498-551)

**Purpose**: Quantifies how quickly EEG signals return to baseline after a distraction event.

**Implementation**:
```python
def compute_recovery_time(eeg_data, stim_times, baseline_window=1.0, 
                          recovery_window=3.0, sampling_rate=256):
    for stim_time in stim_times:
        stim_idx = int(stim_time * sampling_rate)
        baseline_start = int((stim_time - baseline_window) * sampling_rate)
        recovery_end = int((stim_time + recovery_window) * sampling_rate)
        
        # Calculate baseline power
        baseline_power = np.mean(signal_data[baseline_start:stim_idx])
        
        # Set epsilon threshold (10% of baseline)
        epsilon = 0.1 * abs(baseline_power)
        
        # Find first post-stimulus point within epsilon of baseline
        post_stim_signal = signal_data[stim_idx:recovery_end]
        for i, val in enumerate(post_stim_signal):
            if abs(val - baseline_power) < epsilon:
                recovery_time = i / sampling_rate  # Convert to seconds
                break
    
    return np.mean(recovery_times)  # Average across all distractions
```

**Rationale**:
- **Baseline calculation**: 1-second window pre-stimulus establishes participant's resting EEG state
- **Epsilon threshold**: Signal must return within 10% of baseline (not exact value, accounting for natural variability)
- **Recovery window**: 3-second search window post-stimulus
- **Per-channel analysis**: Recovery times computed separately for each channel, then averaged

**Mathematical formulation**:

For each distraction at time $t_s$:

1. **Baseline power**:
$$A_{base} = \frac{1}{T_{base}}\sum_{t=t_s-1s}^{t_s} x(t)$$

2. **Epsilon threshold**:
$$\epsilon = 0.1 \times |A_{base}|$$

3. **Recovery time**:
$$t_{rec} = \min\{t \in [t_s, t_s+3s] : |x(t) - A_{base}| < \epsilon\}$$

4. **Mean recovery time across $N$ distractions**:
$$T_{rec} = \frac{1}{N}\sum_{i=1}^{N} t_{rec,i}$$

**Interpretation**:
- $T_{rec} < 1.0s$: Fast attentional recovery (high resilience)
- $T_{rec} \approx 1.0-2.0s$: Normal attentional recovery
- $T_{rec} > 2.0s$: Slow attentional recovery (low resilience)

**Justification**: The 10% epsilon threshold balances sensitivity (detecting genuine recovery) with specificity (avoiding false positives from noise). This approach is analogous to event-related potential (ERP) baseline correction but applied to continuous power envelopes.

**Novelty**: This epsilon-based recovery metric is a novel contribution of this study. Traditional EEG analysis focuses on static power differences; recovery time captures dynamic attentional flexibility.

---

### 3.5 Behavioral Recovery Time (Lines 460-496)

**Purpose**: Quantifies how quickly reaction times (RT) return to baseline after a distraction.

**Implementation**:
```python
def compute_behavioral_recovery(behavioral_data):
    # Smooth RT with 3-trial moving average
    behavioral_data['rt_smooth'] = behavioral_data['rt'].rolling(window=3, min_periods=1).mean()
    
    recovery_times = []
    for i in range(1, len(behavioral_data)):
        stim = behavioral_data['stimulus'].iloc[i]
        
        # Identify distraction trials (NO-GO stimuli)
        if "NO-GO" in str(stim).upper() or "DISTRACT" in str(stim).upper():
            baseline_rt = behavioral_data['rt_smooth'].iloc[max(0, i-3):i].mean()
            
            # Find when RT returns within 10% of baseline
            for j in range(i+1, len(behavioral_data)):
                if abs(behavioral_data['rt_smooth'].iloc[j] - baseline_rt) < 0.1 * baseline_rt:
                    recovery_time = (j - i) * baseline_rt  # Approx seconds
                    recovery_times.append(recovery_time)
                    break
    
    return np.mean(recovery_times)
```

**Rationale**:
- **RT smoothing**: 3-trial moving average reduces noise from individual trial variability
- **Baseline calculation**: Pre-distraction RT from 3 preceding trials
- **10% threshold**: Consistent with EEG recovery epsilon (within 10% of baseline)
- **Approximation**: `(j - i) * baseline_rt` estimates elapsed time (assumes RT ≈ trial duration)

**Mathematical formulation**:

For each distraction at trial $i$:

1. **Smoothed RT**:
$$RT_{smooth}(i) = \frac{1}{3}\sum_{k=i-2}^{i} RT(k)$$

2. **Baseline RT**:
$$RT_{base}(i) = \frac{1}{3}\sum_{k=i-3}^{i-1} RT_{smooth}(k)$$

3. **Recovery trial**:
$$j_{rec} = \min\{j > i : |RT_{smooth}(j) - RT_{base}(i)| < 0.1 \times RT_{base}(i)\}$$

4. **Recovery time**:
$$t_{rec,behavioral} = (j_{rec} - i) \times RT_{base}(i)$$

**Limitations**:
- **Trial duration approximation**: Assumes trial duration ≈ RT, ignoring ITI (500 ms) and stimulus presentation time
- **More accurate formula**: `(j - i) * (mean_RT + ITI) = (j - i) * (RT + 0.5s)`

**Interpretation**:
- Fast behavioral recovery: RTs stabilize within 1-3 trials
- Slow behavioral recovery: RTs remain elevated for >5 trials

**Justification**: RT is a direct measure of processing speed. Post-distraction RT increases indicate continued attentional disruption (Weissman et al., 2006).

---

### 3.6 Combined Recovery Time (Lines 812-818)

**Implementation**:
```python
if not np.isnan(eeg_recovery_mean) and not np.isnan(behavioral_recovery):
    combined_recovery = 0.5 * eeg_recovery_mean + 0.5 * behavioral_recovery
elif not np.isnan(eeg_recovery_mean):
    combined_recovery = eeg_recovery_mean
else:
    combined_recovery = behavioral_recovery
```

**Rationale**:
- **Multi-modal integration**: Combines neural (EEG) and behavioral (RT) indices
- **Equal weighting**: 50/50 split assumes both measures are equally informative
- **Robustness**: Falls back to available measure if one is missing

**Mathematical formulation**:

$$T_{combined} = \begin{cases}
0.5 \times T_{EEG} + 0.5 \times T_{behavioral} & \text{if both available} \\
T_{EEG} & \text{if only EEG available} \\
T_{behavioral} & \text{if only RT available}
\end{cases}$$

**Justification**: Combined metrics provide more comprehensive assessment than single modality (Berger & Davelaar, 2018). EEG captures covert neural processes; RT captures overt behavioral output.

---

### 3.7 Trials to 3 Consecutive Correct Responses (Lines 396-458)

**Purpose**: Measures behavioral recovery as the number of trials needed to achieve stable performance after a distraction.

**Implementation**:
```python
def compute_trials_to_consecutive_correct(behavioral_data, num_consecutive=3):
    # Find trials with distractions (stim_time not NaN)
    stim_indices = behavioral_data[behavioral_data['stim_time'].notna()].index.tolist()
    
    trials_to_recovery = []
    for stim_idx in stim_indices:
        consecutive_count = 0
        trials_needed = 0
        
        # Look forward from distraction trial
        for i in range(stim_idx + 1, len(behavioral_data)):
            trials_needed += 1
            
            if behavioral_data.loc[i, 'response_correct'] == 1:
                consecutive_count += 1
                if consecutive_count >= 3:
                    trials_to_recovery.append(trials_needed)
                    break
            else:
                consecutive_count = 0  # Reset on incorrect response
    
    return np.mean(trials_to_recovery)
```

**Rationale**:
- **Consecutive correct criterion**: 3 consecutive correct responses indicate stable recovery
- **Reset mechanism**: Counter resets on any incorrect response
- **Direct behavioral index**: No assumptions about RT or trial duration

**Mathematical formulation**:

For each distraction at trial $i$:

$$N_{rec}(i) = \min\{n : \forall k \in [i+n-2, i+n], \ C(k) = 1\}$$

Where:
- $N_{rec}(i)$ = trials to recovery after distraction $i$
- $C(k)$ = correctness of trial $k$ (1 = correct, 0 = incorrect)
- Condition: 3 consecutive trials all correct

**Mean across distractions**:

$$\bar{N}_{rec} = \frac{1}{M}\sum_{i=1}^{M} N_{rec}(i)$$

Where $M$ = number of distractions.

**Interpretation**:
- $\bar{N}_{rec} \leq 3$: Immediate recovery (3 trials = 1.5-2 seconds)
- $\bar{N}_{rec} \approx 4-5$: Quick recovery (~2-3 seconds)
- $\bar{N}_{rec} \approx 6-8$: Moderate recovery (~3-5 seconds)
- $\bar{N}_{rec} > 8$: Slow recovery (>5 seconds)

**Justification**: Consecutive correct responses provide a stringent criterion for recovery, reducing false positives from single lucky guesses. The threshold of 3 balances sensitivity (detecting recovery) with practicality (achievable within the task).

---

## Stage 4: Attention Span Score (ASS) Calculation

### 4.1 Overview (Lines 599-757)

**Purpose**: Integrate multiple behavioral and neural metrics into a single composite score (0-100) representing overall attention span capacity.

**Conceptual Framework**:

$$\text{Attention Span} = f(\text{Behavioral Performance}, \text{Neural Efficiency}, \text{Recovery Capacity})$$

**Implementation Philosophy**:
- **Multi-dimensional**: No single metric captures attention span fully
- **Normalization**: Convert diverse metrics (seconds, percentages, ratios) to common 0-1 scale
- **Weighted average**: Combine normalized metrics with equal or custom weights
- **Scaling**: Transform 0-1 score to 0-100 for interpretability

### 4.2 Metric Components

Five metrics contribute to ASS:

| Metric | Symbol | Direction | Weight | Rationale |
|--------|--------|-----------|--------|-----------|
| **Time to Give In (TTGI)** | $T_{TTGI}$ | Higher = Better | 20% | Persistence under distraction |
| **Accuracy** | $A$ | Higher = Better | 20% | Overall task performance |
| **Reaction Time (RT)** | $RT$ | Lower = Better | 20% | Processing speed |
| **Recovery Lag** | $T_{rec}$ | Lower = Better | 20% | Attentional resilience |
| **EEG Metric (θ/β ratio)** | $R_{\theta/\beta}$ | Lower = Better | 20% | Neural attention state |

**Note**: TTGI is only available if task includes "time to give in" measure (not standard in Go/No-Go tasks). If unavailable, weights are redistributed equally among remaining 4 metrics.

### 4.3 Normalization Procedure

Each metric is normalized to [0, 1] scale using **fixed theoretical ranges** based on literature and pilot data:

#### 4.3.1 TTGI Normalization (Lines 704-708)

**Formula**:
$$\text{TTGI}_{norm} = \min\left(1.0, \frac{T_{TTGI}}{300}\right)$$

**Rationale**:
- **Range**: 0-300 seconds (5 minutes)
- **Assumption**: Maximal persistence = 5 minutes under continuous distraction
- **Capped at 1.0**: Values >300s still score 1.0 (maximum credit)

**Direction**: Higher = better (already aligned with ASS)

#### 4.3.2 Accuracy Normalization (Lines 710-714)

**Formula**:
$$\text{Accuracy}_{norm} = A$$

**Rationale**:
- **Range**: Already 0-1 (0-100%)
- **No transformation needed**

**Direction**: Higher = better (already aligned with ASS)

#### 4.3.3 RT Normalization (Lines 716-721)

**Formula**:
$$\text{RT}_{norm} = \max\left(0, \min\left(1, \frac{RT - 0.2}{1.8}\right)\right)$$

$$\text{RT}_{score} = 1.0 - \text{RT}_{norm}$$

**Rationale**:
- **Range**: 0.2-2.0 seconds
  - **Lower bound (0.2s)**: Faster than this is physiologically implausible (anticipatory)
  - **Upper bound (2.0s)**: Slower than this indicates lapses or disengagement
- **Inversion**: Lower RT is better, so we compute `1 - normalized_RT`

**Literature support**:
- Simple RT: 150-200 ms (Luce, 1986)
- Choice RT (2-alternative): 250-500 ms (Ratcliff & McKoon, 2008)
- Go/No-Go RT: 300-600 ms typical (Nieuwenhuis et al., 2003)
- Lapses: >1500 ms indicates attention failure (Weissman et al., 2006)

**Direction after inversion**: Higher = better (aligned with ASS)

#### 4.3.4 Recovery Lag Normalization (Lines 723-728)

**Formula**:
$$\text{Recovery}_{norm} = \min\left(1.0, \frac{T_{rec}}{3.0}\right)$$

$$\text{Recovery}_{score} = 1.0 - \text{Recovery}_{norm}$$

**Rationale**:
- **Range**: 0-3.0 seconds
  - **Upper bound (3.0s)**: This is the recovery window used in analysis
  - **Assumption**: Recovery >3s indicates sustained attentional disruption
- **Inversion**: Lower recovery time is better

**Direction after inversion**: Higher = better (aligned with ASS)

#### 4.3.5 EEG (θ/β ratio) Normalization (Lines 730-735)

**Formula**:
$$\text{EEG}_{norm} = \max\left(0, \min\left(1, \frac{R_{\theta/\beta} - 0.5}{1.5}\right)\right)$$

$$\text{EEG}_{score} = 1.0 - \text{EEG}_{norm}$$

**Rationale**:
- **Range**: 0.5-2.0
  - **Lower bound (0.5)**: Typical ratio in attentive adults (Monastra et al., 2001)
  - **Upper bound (2.0)**: Elevated ratio indicating ADHD or severe inattention (Snyder & Hall, 2006)
- **Inversion**: Lower θ/β is better (more attention)

**Literature support**:
- Normal adults: θ/β ≈ 0.5-1.2 (Arns et al., 2013)
- ADHD adults: θ/β ≈ 1.5-3.0 (Arns et al., 2013)
- Diagnostic threshold: θ/β > 1.5 (Snyder & Hall, 2006)

**Direction after inversion**: Higher = better (aligned with ASS)

### 4.4 ASS Computation (Lines 738-757)

**Formula**:

$$\text{ASS} = 100 \times \sum_{i=1}^{N} w_i \cdot m_i$$

Where:
- $m_i$ = normalized metric $i$ (0-1 scale, all oriented "higher = better")
- $w_i$ = weight for metric $i$ (default: $w_i = 1/N$, equal weighting)
- $N$ = number of available metrics (4 or 5, depending on TTGI availability)

**Default weights (equal)**:
$$w_{TTGI} = w_{Accuracy} = w_{RT} = w_{Recovery} = w_{EEG} = 0.20$$

**Custom weights** (optional):
Users can specify custom weights via dictionary:
```python
weights = {
    'TTGI': 0.25,
    'Accuracy': 0.25,
    'RT': 0.15,
    'RecoveryLag': 0.20,
    'EEG': 0.15
}
```

**Justification for equal weights**:
- **Theoretical agnosticism**: No strong a priori reason to weight one metric over others
- **Empirical approach**: Equal weights allow data to reveal relative importance
- **Interpretability**: Simple model is easier to explain and replicate
- **Future refinement**: Weights can be optimized via regression or factor analysis once normative data are collected

### 4.5 ASS Interpretation

**Score ranges** (Lines 1447-1457):

| ASS Range | Interpretation | Cognitive State |
|-----------|----------------|-----------------|
| **80-100** | Excellent attention span | Superior sustained attention and inhibitory control |
| **65-79** | Good attention span | Above-average performance with minor lapses |
| **50-64** | Average attention span | Typical adult performance |
| **35-49** | Below average attention span | Frequent lapses and distractibility |
| **0-34** | Poor attention span | Severe attentional difficulties |

**Validity considerations**:
- **Face validity**: High ASS requires good performance across multiple dimensions
- **Discriminant validity**: ASS should distinguish attentive from inattentive individuals
- **Clinical utility**: ASS <50 may indicate need for intervention (analogous to IQ <85)

**Limitations**:
- **Fixed ranges**: Normalization ranges based on literature may not generalize to all populations
- **Population specificity**: Norms developed on [*age range, N*] may not apply to children or elderly
- **Task specificity**: ASS reflects attention in Go/No-Go context; may not generalize to other attention paradigms

---

## Stage 5: Data Synchronization and Validation

### 5.1 Timestamp Synchronization Problem

**Challenge** (Lines 1689-1836):

- **CSV files**: Contain only trial indices (1-200) and RTs; no absolute timestamps
- **XDF files**: Contain continuous Unix timestamps (e.g., 1758310310.738) at 256 Hz
- **Manual distraction logs**: Human-readable times (e.g., "1:30 PM")

**Goal**: Align distraction times with specific CSV trial indices and XDF sample indices for recovery analysis.

### 5.2 Synchronization Algorithm

#### Step 1: Parse Human-Readable Times (Lines 1584-1612)

**Implementation**:
```python
def parse_time_to_seconds(time_str):
    from datetime import datetime
    time_str = time_str.strip().lower().replace(' ', '')
    time_obj = datetime.strptime(time_str, '%I:%M%p').time()
    total_seconds = time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second
    return total_seconds
```

**Example**:
- Input: "1:30pm"
- Output: 48,600 seconds (from midnight)

#### Step 2: Convert to Relative Times (Lines 1614-1625)

**Implementation**:
```python
def convert_times_to_relative(time_list):
    sorted_times = sorted(time_list)
    baseline_time = sorted_times[0]
    relative_times = [(t - baseline_time) for t in sorted_times]
    return relative_times
```

**Example**:
- Input: [48600, 48660, 48720] (1:30pm, 1:31pm, 1:32pm)
- Output: [0, 60, 120] (seconds from first distraction)

#### Step 3: Match XDF Timestamps (Lines 1789-1816)

**Implementation**:
```python
def find_closest_timestamp_match(target_unix_time, xdf_timestamps, tolerance=60):
    differences = np.abs(np.array(xdf_timestamps) - target_unix_time)
    min_diff_idx = np.argmin(differences)
    min_diff = differences[min_diff_idx]
    
    if min_diff <= tolerance:
        return min_diff_idx, min_diff
    else:
        return None, min_diff

# For each distraction:
first_xdf_time = xdf_timestamps[0]
absolute_stimulus_time = first_xdf_time + relative_time
xdf_idx, time_diff = find_closest_timestamp_match(absolute_stimulus_time, xdf_timestamps)
```

**Algorithm**:
1. Get first XDF timestamp (session start reference)
2. Add relative distraction time to get absolute Unix time
3. Find closest XDF sample within ±60s tolerance
4. Return XDF sample index

**Example**:
- First XDF time: 1758310310.738 (Unix timestamp)
- Relative distraction: 60 seconds
- Target time: 1758310370.738
- Closest XDF sample: index 15,360 (60s × 256 Hz)

#### Step 4: Estimate CSV Trial Index (Lines 1805-1810)

**Implementation**:
```python
trial_duration_estimate = len(xdf_timestamps) / len(csv_trials)
estimated_trial_idx = int(xdf_idx / trial_duration_estimate)
estimated_trial_idx = max(0, min(estimated_trial_idx, len(csv_trials) - 1))
```

**Algorithm**:
1. Estimate average trial duration in XDF samples: `total_samples / total_trials`
2. Convert XDF index to trial index: `xdf_idx / samples_per_trial`
3. Clamp to valid range [0, num_trials-1]

**Example**:
- XDF samples: 51,200 (200 seconds at 256 Hz)
- CSV trials: 200
- Samples per trial: 256 (1 second average)
- XDF index: 15,360 → Trial index: 60

#### Step 5: Mark CSV with Distraction Times (Lines 1810-1822)

**Implementation**:
```python
csv_data.loc[estimated_trial_idx, 'stim_time'] = relative_time
csv_data.to_csv(filepath, index=False)
```

**Result**: CSV now has `stim_time` column with distraction timestamps (in seconds from first distraction).

### 5.3 Synchronization Limitations

**Sources of error**:

1. **Recording start lag**: 1-2 second gap between LSL recording start and first trial
   - **Impact**: ±1-2 trial index error
   - **Mitigation**: Manual verification of distraction timing during experiment

2. **Variable trial durations**: RTs range 0.2-2.0 seconds; trials are not evenly spaced
   - **Impact**: Cumulative timing drift over 200 trials
   - **Mitigation**: Use RT-corrected trial duration estimates (future improvement)

3. **Manual timestamp recording**: Human reaction time in recording distraction time
   - **Impact**: ±1-2 second error per distraction
   - **Mitigation**: Use automated distraction delivery system (future improvement)

**Validation**:
- Distraction times cross-referenced with experimenter notes
- Visual inspection of EEG time series at expected distraction points
- Outlier detection: distractions <10 trials or >190 trials flagged for review

---

## Statistical Analysis

### Descriptive Statistics

**Per-subject, per-condition metrics**:
- Mean ± SD for accuracy, RT, theta/beta ratio, alpha/beta ratio, recovery time
- ASS score with interpretation

**Cross-condition comparisons**:
- Set 1 (Baseline) vs. Set 2 (Distraction+Response) vs. Set 3 (Distraction+NoResponse)
- Within-subjects repeated measures design

### Inferential Statistics

[*Note: Add based on your actual analysis*]

**Potential analyses**:
1. **Repeated measures ANOVA**: Effect of condition (Set) on ASS, accuracy, RT, recovery time
2. **Post-hoc tests**: Pairwise comparisons (Bonferroni-corrected)
3. **Effect sizes**: Cohen's d or partial η² for condition effects
4. **Correlations**: Relationship between EEG metrics and behavioral metrics
5. **Regression**: Predictors of ASS (which metrics drive composite score?)

**Software**: 
- Python: `scipy.stats`, `statsmodels`, `pingouin`
- R: `ez`, `afex`, `lme4` (if mixed models used)

---

## Data Quality and Exclusions

### EEG Quality Metrics

**Artifact rejection rate**:
- Basic preprocessing: [*X%*] of samples rejected (>500 μV)
- Advanced preprocessing: [*Y%*] of samples rejected (>100 μV + ICA + Z>4)

**ICA artifact components**:
- Mean [*M*] components identified as artifacts per session (SD = [*S*])
- Common artifacts: eye blinks (frontal channels), muscle tension (temporal channels)

**Signal-to-noise ratio**:
- Calculated as: $SNR = 10 \log_{10}(\sigma_{signal}^2 / \sigma_{noise}^2)$
- Mean SNR: [*X*] dB (acceptable range: >10 dB)

### Behavioral Quality Metrics

**Exclusion criteria** (if any):
- Accuracy <50% (below chance for 2-alternative tasks)
- RT <0.1s on >10% of trials (anticipatory responding)
- RT >5.0s on >10% of trials (attentional lapses)

**Actual exclusions**: [*N subjects excluded, reason*]

---

## Software and Reproducibility

### Analysis Pipeline

**Code repository**: [*GitHub URL*]

**Key scripts**:
- `unified_eeg_analysis.py`: Main analysis pipeline (2050 lines)
- `Classic_task1.py`, `SART_task2.py`, `semantic_task3.py`: Task scripts
- `requirements.txt`: Python dependencies

**Dependencies**:
```
psychopy >= 2023.1.0
pylsl >= 1.16.0
pandas >= 2.0.0
numpy >= 1.24.0
scipy >= 1.10.0
scikit-learn >= 1.2.0
matplotlib >= 3.7.0
seaborn >= 0.12.0
```

### Computational Environment

**Hardware**: [*CPU, RAM, OS*]

**Software**:
- Python 3.9+ (Anaconda distribution)
- Jupyter Notebook 6.5+ (for interactive analysis)

**Execution time**:
- Basic preprocessing: ~10 seconds per session
- Advanced preprocessing: ~30 seconds per session (includes ICA)
- Full 9-session analysis: ~5 minutes per subject

**Reproducibility**:
- Random seed: `random_state=42` for ICA and any stochastic operations
- XDF/CSV file hashes: MD5 checksums recorded for data integrity
- Analysis timestamp: Logged in output files

---

## Visualization

### Generated Figures (per session)

1. **EEG Dashboard** (Lines 1232-1373):
   - Raw EEG time series (4 channels)
   - Frequency band powers by channel
   - Alpha/beta and theta/beta ratios
   - Reaction time distribution
   - Accuracy over time (10-trial moving average)
   - Frontal alpha asymmetry

2. **Recovery Summary Bar Chart** (Lines 1011-1074):
   - EEG recovery time per channel
   - Behavioral recovery time
   - Combined recovery time
   - Color-coded bars with value labels

3. **Recovery Time Series** (Lines 1076-1230):
   - Top panel: Individual trial epochs around distractions
   - Bottom panel: Average epoch with ±1 SD confidence interval
   - Baseline, epsilon bounds, and recovery points marked
   - Visual validation of epsilon-based recovery detection

### Summary Tables (Lines 1890-2046)

**Detailed results table** (per subject):
- Rows: 9 sessions (3 sets × 3 tasks)
- Columns: ASS, Accuracy, RT (mean ± SD), Theta/Beta, Alpha/Beta, Recovery Time, Trials to 3 Consecutive Correct, Frontal Asymmetry

**Cross-set comparison table**:
- Rows: 3 sets (Baseline, Distraction+Response, Distraction+NoResponse)
- Columns: Mean ± SD for ASS, Accuracy, RT, Recovery Time
- Distraction impact analysis: Δ from baseline

---

## Novel Contributions of This Analysis Approach

1. **Epsilon-based EEG recovery metric**: Dynamic attention recovery quantification (not in standard EEG literature)

2. **Multi-modal recovery integration**: Combining EEG and behavioral recovery times for comprehensive assessment

3. **Trials to consecutive correct**: Behavioral recovery criterion resistant to noise

4. **Composite ASS metric**: Integrating 5 dimensions of attention into interpretable 0-100 score

5. **Real-time synchronization**: LSL-based event marking with post-hoc timestamp alignment

6. **Distraction protocol**: Systematic comparison of distraction conditions (response required vs. ignored)

---

## Limitations and Future Directions

### Current Limitations

1. **Fixed normalization ranges**: May not generalize to all populations
2. **Equal ASS weights**: Not empirically optimized
3. **Estimation-based CSV-XDF sync**: Lacks ground-truth trial timestamps
4. **Limited channels**: 4-channel Muse vs. 32/64-channel research systems
5. **Dry electrodes**: Lower signal quality than wet electrodes

### Planned Improvements

1. **Adaptive normalization**: Population-specific ranges based on normative data
2. **Empirical weight optimization**: Regression or factor analysis to derive optimal ASS weights
3. **Direct trial timestamps**: Modify task scripts to log Unix timestamps per trial
4. **Expanded montage**: Test with higher-density EEG systems
5. **Machine learning**: Train classifiers to predict attention state from EEG features

---

## References

Arns, M., Conners, C. K., & Kraemer, H. C. (2013). A decade of EEG theta/beta ratio research in ADHD: A meta-analysis. *Journal of Attention Disorders*, *17*(5), 374-383.

Berger, A., & Davelaar, E. J. (2018). Frontal alpha oscillations and attentional control: A virtual reality neurofeedback study. *Neuroscience*, *378*, 189-197.

Borghini, G., Astolfi, L., Vecchiato, G., Mattia, D., & Babiloni, F. (2014). Measuring neurophysiological signals in aircraft pilots and car drivers for the assessment of mental workload, fatigue and drowsiness. *Neuroscience & Biobehavioral Reviews*, *44*, 58-75.

Davidson, R. J. (2004). What does the prefrontal cortex "do" in affect: Perspectives on frontal EEG asymmetry research. *Biological Psychology*, *67*(1-2), 219-234.

Delorme, A., Sejnowski, T., & Makeig, S. (2007). Enhanced detection of artifacts in EEG data using higher-order statistics and independent component analysis. *NeuroImage*, *34*(4), 1443-1449.

Engel, A. K., & Fries, P. (2010). Beta-band oscillations—signalling the status quo? *Current Opinion in Neurobiology*, *20*(2), 156-165.

Harmon-Jones, E., Gable, P. A., & Peterson, C. K. (2010). The role of asymmetric frontal cortical activity in emotion-related phenomena: A review and update. *Biological Psychology*, *84*(3), 451-462.

Jung, T. P., Makeig, S., Humphries, C., Lee, T. W., Mckeown, M. J., Iragui, V., & Sejnowski, T. J. (2000). Removing electroencephalographic artifacts by blind source separation. *Psychophysiology*, *37*(2), 163-178.

Klimesch, W. (2012). Alpha-band oscillations, attention, and controlled access to stored information. *Trends in Cognitive Sciences*, *16*(12), 606-617.

Luce, R. D. (1986). *Response Times: Their Role in Inferring Elementary Mental Organization*. Oxford University Press.

Luck, S. J. (2014). *An Introduction to the Event-Related Potential Technique* (2nd ed.). MIT Press.

Makeig, S., Bell, A. J., Jung, T. P., & Sejnowski, T. J. (1996). Independent component analysis of electroencephalographic data. *Advances in Neural Information Processing Systems*, *8*, 145-151.

Monastra, V. J., Lubar, J. F., & Linden, M. (2001). The development of a quantitative electroencephalographic scanning process for attention deficit-hyperactivity disorder: Reliability and validity studies. *Neuropsychology*, *15*(1), 136-144.

Nieuwenhuis, S., Yeung, N., Van Den Wildenberg, W., & Ridderinkhof, K. R. (2003). Electrophysiological correlates of anterior cingulate function in a go/no-go task: Effects of response conflict and trial type frequency. *Cognitive, Affective, & Behavioral Neuroscience*, *3*(1), 17-26.

Nunez, P. L., & Srinivasan, R. (2006). *Electric Fields of the Brain: The Neurophysics of EEG* (2nd ed.). Oxford University Press.

Pfurtscheller, G., & Lopes da Silva, F. H. (1999). Event-related EEG/MEG synchronization and desynchronization: Basic principles. *Clinical Neurophysiology*, *110*(11), 1842-1857.

Ratcliff, R., & McKoon, G. (2008). The diffusion decision model: Theory and data for two-choice decision tasks. *Neural Computation*, *20*(4), 873-922.

Snyder, S. M., & Hall, J. R. (2006). A meta-analysis of quantitative EEG power associated with attention-deficit hyperactivity disorder. *Journal of Clinical Neurophysiology*, *23*(5), 440-455.

Weissman, D. H., Roberts, K. C., Visscher, K. M., & Woldorff, M. G. (2006). The neural bases of momentary lapses in attention. *Nature Neuroscience*, *9*(7), 971-978.

Widmann, A., Schröger, E., & Maess, B. (2015). Digital filter design for electrophysiological data–a practical approach. *Journal of Neuroscience Methods*, *250*, 34-46.

---

## Supplementary Materials

**Suggested supplementary files**:
1. Full analysis pipeline flowchart
2. Sample XDF/CSV data files (de-identified)
3. Complete results tables for all subjects
4. Parameter sensitivity analysis (effect of epsilon threshold, filter cutoffs, etc.)
5. Code repository with example usage

---

**Document Created**: [Date]
**Last Updated**: [Date]
**Version**: 1.0
**Corresponding Analysis Code**: `unified_eeg_analysis.py` (v1.0, [date])

