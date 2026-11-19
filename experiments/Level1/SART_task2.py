from psychopy import visual, core, event
from pylsl import StreamOutlet, StreamInfo
import random
import csv
import os
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SUBJECT_ID = 2
SET_ID = 1

# ---------------------
# 1. LSL Marker Setup
# ---------------------
info = StreamInfo(name='Markers', type='Markers', channel_count=3, nominal_srate=0, channel_format='float32')
outlet = StreamOutlet(info)

# ---------------------
# 2. SART Stimuli (Sustained Attention to Response Task)
# ---------------------
# Numbers 1-9, where participants press spacebar for all numbers EXCEPT 3
numbers = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
stimuli = []

# Create exactly 50 trials with randomly selected numbers
for _ in range(100):
    num = random.choice(numbers)  # Randomly select a number for each trial
    if num == '3':
        stimuli.append((num, 0))  # 0 = no-go (don't press spacebar for 3)
    else:
        stimuli.append((num, 1))  # 1 = go (press spacebar for non-3 numbers)

random.shuffle(stimuli)

# ---------------------
# 3. PsychoPy Setup
# ---------------------
win = visual.Window([1200, 800], color='black', units='pix')
text_stim = visual.TextStim(win, text='', color='white', height=60)

# ---------------------
# 4. Instructions text
# ---------------------
instruction_text = visual.TextStim(win, text='', color='white', height=28, wrapWidth=1000)

# ---------------------
# 5. Show Instructions
# ---------------------
instructions = """
SART - SUSTAINED ATTENTION TO RESPONSE TASK
=============================================

Numbers from 1 to 9 will appear on the screen.

YOUR TASK:
• Press SPACEBAR for ALL numbers EXCEPT 3
• Press ANY OTHER KEY when you see the number 3

Remember: DO NOT press spacebar when you see 3!

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
# 7. Trial loop
# ---------------------
for stim, correct in stimuli:
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
    # For non-3 numbers (correct=1): spacebar is correct
    # For number 3 (correct=0): any key except spacebar is correct
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
# 6. Save results to CSV with unique filename
# ---------------------
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
out_dir = os.path.join(SCRIPT_DIR, "Results_CSV", f"Subject{SUBJECT_ID}")
os.makedirs(out_dir, exist_ok=True)
filename = os.path.join(out_dir, f"SART_results_set{SET_ID}_{timestamp}.csv")

with open(filename, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['timestamp', 'stimulus', 'stimulus_type', 'response', 'response_correct', 'rt'])
    writer.writeheader()
    writer.writerows(results)

print(f"SART Experiment finished. Results saved to {filename}. All markers sent to LSL.")
