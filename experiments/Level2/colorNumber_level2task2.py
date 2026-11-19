"""
Color-Number Go/No-Go Task - Level 2 Task 2
============================================
Screen shows a number (0-9) in different colors.
Players press SPACEBAR only when the number-color combination matches the rule:
    "Press SPACEBAR if the number is EVEN AND the color is RED"
Otherwise press any other key.

This task requires dual-feature processing (number AND color).
"""

from psychopy import visual, core, event
from pylsl import StreamOutlet, StreamInfo
import random
import csv
from datetime import datetime
import os

# ---------------------
# 1. LSL Marker Setup - send markers to LSL stream
# ---------------------
info = StreamInfo(name='Markers', type='Markers', channel_count=3, nominal_srate=0, channel_format='float32')
outlet = StreamOutlet(info)

# ---------------------
# 2. Stimuli Setup - Numbers and Colors
# ---------------------
# Numbers: 0-9
NUMBERS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
EVEN_NUMBERS = ['0', '2', '4', '6', '8']
ODD_NUMBERS = ['1', '3', '5', '7', '9']

# Colors with their names and hex values
COLORS = {
    'RED': '#FF0000',
    'BLUE': '#0066FF',
    'GREEN': '#00CC00',
    'YELLOW': '#FFFF00',
    'PURPLE': '#9933FF',
    'ORANGE': '#FF6600'
}

# Target: EVEN number AND RED color
TARGET_COLOR = 'RED'

# Create trial list - 100 trials
trial_number = 100
stimuli = []

for _ in range(trial_number):
    number = random.choice(NUMBERS)
    color_name = random.choice(list(COLORS.keys()))
    
    # Determine if this is a go trial (even AND red)
    is_even = number in EVEN_NUMBERS
    is_red = color_name == TARGET_COLOR
    
    if is_even and is_red:
        correct = 1  # Go trial - press spacebar
    else:
        correct = 0  # No-go trial - press other key
    
    stimuli.append({
        'number': number,
        'color_name': color_name,
        'color_hex': COLORS[color_name],
        'correct': correct
    })

random.shuffle(stimuli)

# ---------------------
# 3. PsychoPy Setup - window and visual stimuli
# ---------------------
win = visual.Window([1200, 800], color='black', units='pix')

# Number display
number_stim = visual.TextStim(win, text='', color='white', height=150, bold=True)

# Color indicator text (shown below number)
color_label = visual.TextStim(win, text='', color='white', height=30, pos=(0, -150))

# Instructions text
instruction_text = visual.TextStim(win, text='', color='white', height=28, wrapWidth=1000)

# Rule reminder at top of screen
rule_reminder = visual.TextStim(win, text='RULE: SPACEBAR if EVEN + RED', 
                                 color='gray', height=20, pos=(0, 350))

# ---------------------
# 4. Show Instructions
# ---------------------
instructions = """
COLOR-NUMBER GO/NO-GO TASK
===========================

You will see numbers (0-9) displayed in different colors.

THE RULE:
Press SPACEBAR ONLY if:
    • The number is EVEN (0, 2, 4, 6, 8)
    AND
    • The color is RED

Press ANY OTHER KEY for all other combinations.

Examples:
• "4" in RED → Press SPACEBAR ✓
• "3" in RED → Press other key (odd number)
• "6" in BLUE → Press other key (not red)
• "7" in GREEN → Press other key (odd + not red)

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
# 5. Results storage
# ---------------------
results = []

# ---------------------
# 6. Trial loop - Color-Number Task
# ---------------------
for trial in stimuli:
    # Get current timestamp
    trial_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    number = trial['number']
    color_name = trial['color_name']
    color_hex = trial['color_hex']
    correct = trial['correct']
    
    # Display the number in the specified color
    number_stim.text = number
    number_stim.color = color_hex
    number_stim.draw()
    
    # Show color name below (helps with color-blind accessibility)
    color_label.text = f"({color_name})"
    color_label.color = color_hex
    color_label.draw()
    
    win.flip()
    
    # Start timing for RT
    trial_clock = core.Clock()
    
    # Wait for key press
    keys = event.waitKeys()
    
    if 'escape' in keys:
        break
    
    response = keys[0]
    rt = trial_clock.getTime()
    
    # Clear screen immediately after response
    win.flip()
    
    # Determine if response is correct
    # For go trials (even + red, correct=1): spacebar is correct
    # For no-go trials (correct=0): any key except spacebar is correct
    response_correct = 1 if (response == 'space' and correct == 1) or (response != 'space' and correct == 0) else 0
    
    # Send marker: [stimulus_type, response_correct, reaction_time]
    outlet.push_sample([correct, response_correct, rt])
    
    # Store result for CSV export
    results.append({
        'timestamp': trial_timestamp,
        'stimulus': f"{number}_{color_name}",
        'number': number,
        'color': color_name,
        'stimulus_type': correct,
        'response': response,
        'response_correct': response_correct,
        'rt': rt
    })
    
    core.wait(0.5)  # 500 ms ITI

win.close()

# ---------------------
# 7. Save results to CSV
# ---------------------
# Create Results folder if it doesn't exist
os.makedirs('Results_CSV/Level2', exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f'Results_CSV/Subject38/colorNumber_results_set3_{timestamp}.csv'

with open(filename, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['timestamp', 'stimulus', 'number', 'color', 'stimulus_type', 'response', 'response_correct', 'rt'])
    writer.writeheader()
    writer.writerows(results)

print(f"Color-Number Task finished. Results saved to {filename}. All markers sent to LSL.")
