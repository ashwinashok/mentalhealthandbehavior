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
# 1. LSL Marker Setup - send markers to LSL stream
# ---------------------
info = StreamInfo(name='Markers', type='Markers', channel_count=3, nominal_srate=0, channel_format='float32')
outlet = StreamOutlet(info)

# ---------------------
# 2. Semantic Stimuli - real words vs non-words (pseudowords)
# ---------------------
# Real words vs non-words (pseudowords)
real_words = ['apple', 'banana', 'table', 'chair', 'house', 'water', 'green', 'happy', 'computer', 'music']
non_words = ['blzrk', 'snatp', 'tibdrt', 'glwme', 'flyrp', 'esrto', 'grimpth', 'blintk', 'plvffin', 'worblqx']

# Create exactly 50 trials with randomly selected words
all_words = real_words + non_words  # Combine all possible stimuli
stimuli = []

for _ in range(100):
    word = random.choice(all_words)  # Randomly select a word for each trial
    if word in real_words:
        stimuli.append((word, 1))  # 1 = real word (press spacebar)
    else:
        stimuli.append((word, 0))  # 0 = non-word (don't press spacebar)

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
SEMANTIC TASK - WORD VS NON-WORD
=================================

Words will appear on the screen.
Some are REAL words, some are FAKE words (gibberish).

YOUR TASK:
• Press SPACEBAR when you see a REAL word
  (like: apple, banana, table, chair, house)
• Press ANY OTHER KEY when you see a FAKE word
  (like: blzrk, snatp, tibdrt, glwme)

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
# 7. Trial loop - Semantic Task
#  1. Stimulus presentation - (stimulus_type, correct) - 1 if correct, 0 if incorrect
#  2. Response time measurement - (reaction_time) - time between stimulus presentation and response
#  3. Response correctness evaluation - (correct, response_correct) - 1 if correct, 0 if incorrect
#  4. Marker sending to LSL - (correct, response_correct, reaction_time) - 1 if correct, 0 if incorrect, reaction_time
#  5. ITI (Inter-Trial Interval) - time between trials (500ms)
# ---------------------
for stim, correct in stimuli:
    # Get current timestamp
    trial_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    # Present stimulus on black background
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
    # For real words (correct=1): spacebar is correct
    # For non-words (correct=0): any key except spacebar is correct
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
filename = os.path.join(out_dir, f"semantic_results_set{SET_ID}_{timestamp}.csv")

with open(filename, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['timestamp', 'stimulus', 'stimulus_type', 'response', 'response_correct', 'rt'])
    writer.writeheader()
    writer.writerows(results)

print(f"Semantic Experiment finished. Results saved to {filename}. All markers sent to LSL.")
