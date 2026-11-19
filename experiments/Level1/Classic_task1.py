from psychopy import visual, core, event
from pylsl import StreamOutlet, StreamInfo
import random
import csv
import os
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SUBJECT_ID = 2   # change per participant
SET_ID = 1       # 1=baseline, 2=respond, 3=glance-only

# ---------------------
# 1. LSL Marker Setup - send markers to LSL stream
# ---------------------
info = StreamInfo(name='Markers', type='Markers', channel_count=3, nominal_srate=0, channel_format='float32')
outlet = StreamOutlet(info)

# ---------------------
# 2. Go/No-Go list - 1 if correct, 0 if incorrect
# ---------------------
go_stimuli = ['SPACE', 'GO']
no_go_stimuli = ['NO-GO', 'NOT SPACE']
stimuli = [(s, 1) for s in go_stimuli] + [(s, 0) for s in no_go_stimuli]  # 1=go, 0=no-go
random.shuffle(stimuli)

# ---------------------
# DEBRA CODE
# Option for 50 stimuli
#
# Create a arbitrary element long list randomly composed of go or no_go stimuli
# ---------------------
trial_number = 100
n_element_list = [stimuli[random.randint(0,3)] for i in range(trial_number)]

# ---------------------
# 3. PsychoPy Setup - window and text stimulus
# ---------------------
win = visual.Window([1200, 800], color='black', units='pix')
text_stim = visual.TextStim(win, text='', color='white', height=40)

# ---------------------
# 4. Instructions text
# ---------------------
instruction_text = visual.TextStim(win, text='', color='white', height=28, wrapWidth=1000)

# ---------------------
# 5. Show Instructions
# ---------------------
instructions = """
CLASSIC GO/NO-GO TASK
======================

Words will appear on the screen one at a time.

YOUR TASK:
• Press SPACEBAR when you see "SPACE" or "GO"
• Press ANY OTHER KEY when you see "NO-GO" or "NOT SPACE"

Press SPACEBAR to begin...
"""

instruction_text.text = instructions
instruction_text.draw()
win.flip()
event.waitKeys(keyList=['space'])

# Short countdown
for i in [3, 2, 1]:
    instruction_text.text = str(i)
    instruction_text.draw()
    win.flip()
    core.wait(1.0)

# ---------------------
# 6. Results storage - collect results for CSV export
# ---------------------
results = []

# ---------------------
# 7. Trial loop - Classic Go/No-Go Paradigm
#  1. Stimulus presentation - (stimulus_type, correct) - 1 if correct, 0 if incorrect
#  2. Response time measurement - (reaction_time) - time between stimulus presentation and response
#  3. Response correctness evaluation - (correct, response_correct) - 1 if correct, 0 if incorrect
#  4. Marker sending to LSL - (correct, response_correct, reaction_time) - 1 if correct, 0 if incorrect, reaction_time
#  5. ITI (Inter-Trial Interval) - time between trials (500ms)
# ---------------------
#
# Change 'stimuli' in following loop to be 'fifty_element_list' to have 50 trials
#
for stim, correct in n_element_list:
    # Get current timestamp
    trial_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    text_stim.text = stim
    text_stim.draw()
    win.flip()
    
    # Start timing for RT
    trial_clock = core.Clock()
    
    # Wait for key press
    keys = event.waitKeys()
    
    if 'escape' in keys:
        break
    
    response = keys[0]
    rt = trial_clock.getTime()
    
    # Clear screen immediately after response - show only black background
    win.flip()  # This clears the text and shows just black background
    
    # Determine if response is correct
    # For go trials (correct=1): spacebar is correct
    # For no-go trials (correct=0): any key except spacebar is correct
    response_correct = 1 if (response == 'space' and correct == 1) or (response != 'space' and correct == 0) else 0
    
    # Send marker: [stimulus_type, response_correct, reaction_time]
    outlet.push_sample([correct, response_correct, rt])
    
    # Store result for CSV export
    results.append({
        'timestamp': trial_timestamp,
        'stimulus': stim,
        'stimulus_type': correct,
        'response': response,
        'response_correct': response_correct,
        'rt': rt
    })
    
    core.wait(0.5)  # 500 ms ITI

win.close()

# ---------------------
# 6. Save results to CSV with unique filename in Results folder
# ---------------------
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
out_dir = os.path.join(SCRIPT_DIR, "Results_CSV", f"Subject{SUBJECT_ID}")
os.makedirs(out_dir, exist_ok=True)
filename = os.path.join(out_dir, f"Classic_results_set{SET_ID}_{timestamp}.csv")

with open(filename, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['timestamp', 'stimulus', 'stimulus_type', 'response', 'response_correct', 'rt'])
    writer.writeheader()
    writer.writerows(results)

print(f"Experiment finished. Results saved to {filename}. All markers sent to LSL.")
