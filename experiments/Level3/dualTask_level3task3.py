"""
Dual-Task Updating Game (N-back Modified) - Level 3 Task 3
============================================================
Two streams of items appear simultaneously:
    - LEFT SIDE: Numbers (0-9)
    - RIGHT SIDE: Shapes (circle, square, triangle, etc.)

Participants must follow TWO rules simultaneously:
    Rule 1: Press 'N' if the current number is LARGER than the previous number
    Rule 2: Press 'S' if the current shape MATCHES the shape from 2 steps earlier (2-back)

If BOTH conditions are met: Press SPACEBAR
If NEITHER condition is met: Press any other key

This task measures dual-task performance and working memory updating.
"""

from psychopy import visual, core, event
import numpy as np
try:
    from pylsl import StreamOutlet, StreamInfo
    PYLSL_INSTALLED = True
except ImportError:
    print("pylsl not installed. LSL markers will be disabled.")
    PYLSL_INSTALLED = False
import random
import csv
from datetime import datetime
import os

# ---------------------
# 1. LSL Marker Setup - send markers to LSL stream
# ---------------------
LSL_AVAILABLE = False
outlet = None
if PYLSL_INSTALLED:
    try:
        info = StreamInfo(name='Markers', type='Markers', channel_count=3, nominal_srate=0, channel_format='float32')
        outlet = StreamOutlet(info)
        LSL_AVAILABLE = True
    except Exception as e:
        print(f"LSL not available: {e}. Continuing without markers.")

# ---------------------
# 2. Get script directory for relative paths
# ---------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------
# 3. Stimuli Configuration
# ---------------------
NUMBERS = list(range(10))  # 0-9
SHAPES = ['circle', 'square', 'triangle', 'diamond', 'pentagon']

# Task parameters
TRIAL_NUMBER = 100  # Total number of trials
STIMULUS_DURATION = None  # Wait for response

# N-back level for shapes (2-back)
N_BACK = 2

# Probability adjustments to balance trial types
# Slightly increase target probability to ensure enough target trials
NUMBER_INCREASE_PROB = 0.35  # Probability that number increases
SHAPE_MATCH_PROB = 0.30  # Probability of 2-back shape match

# ---------------------
# 4. Generate Stimuli Sequence
# ---------------------
def generate_sequence(num_trials, n_back):
    """Generate a sequence of numbers and shapes with controlled target probabilities"""
    sequence = []
    
    for i in range(num_trials):
        # Generate number
        if i == 0:
            number = random.randint(1, 8)  # First number (avoid extremes)
        else:
            prev_number = sequence[-1]['number']
            if random.random() < NUMBER_INCREASE_PROB:
                # Make it larger
                if prev_number < 9:
                    number = random.randint(prev_number + 1, 9)
                else:
                    number = random.randint(0, 8)
            else:
                # Make it smaller or equal
                number = random.randint(0, prev_number)
        
        # Generate shape
        if i < n_back:
            # First n trials: random shape
            shape = random.choice(SHAPES)
        else:
            # Check if we should create a 2-back match
            if random.random() < SHAPE_MATCH_PROB:
                # Match the shape from n_back steps ago
                shape = sequence[i - n_back]['shape']
            else:
                # Different shape than n_back steps ago
                prev_shape = sequence[i - n_back]['shape']
                available_shapes = [s for s in SHAPES if s != prev_shape]
                shape = random.choice(available_shapes)
        
        sequence.append({
            'trial': i + 1,
            'number': number,
            'shape': shape
        })
    
    return sequence

# Generate sequence
stimuli = generate_sequence(TRIAL_NUMBER, N_BACK)

# ---------------------
# 5. PsychoPy Setup
# ---------------------
win = visual.Window([1200, 800], color='black', units='pix')

# Number display (left side)
number_text = visual.TextStim(win, text='', color='white', height=120, pos=(-200, 0), bold=True)
number_label = visual.TextStim(win, text='NUMBER', color='gray', height=24, pos=(-200, 150))

# Helper function to create vertices for shapes (workaround for PsychoPy bug)
def make_circle_vertices(radius, n_points=32):
    angles = np.linspace(0, 2*np.pi, n_points, endpoint=False)
    return [(radius * np.cos(a), radius * np.sin(a)) for a in angles]

def make_polygon_vertices(radius, n_sides):
    angles = np.linspace(0, 2*np.pi, n_sides, endpoint=False) - np.pi/2
    return [(radius * np.cos(a), radius * np.sin(a)) for a in angles]

def make_rect_vertices(width, height):
    hw, hh = width/2, height/2
    return [(-hw, -hh), (-hw, hh), (hw, hh), (hw, -hh)]

# Shape display (right side) - use ShapeStim with explicit vertices to avoid PsychoPy bug
circle_stim = visual.ShapeStim(win, vertices=make_circle_vertices(60), fillColor='cyan', lineColor='white', lineWidth=3, pos=(200, 0), closeShape=True)
square_stim = visual.ShapeStim(win, vertices=make_rect_vertices(100, 100), fillColor='cyan', lineColor='white', lineWidth=3, pos=(200, 0), closeShape=True)
triangle_stim = visual.ShapeStim(win, vertices=make_polygon_vertices(70, 3), fillColor='cyan', lineColor='white', lineWidth=3, pos=(200, 0), closeShape=True)
diamond_stim = visual.ShapeStim(win, vertices=make_polygon_vertices(70, 4), fillColor='cyan', lineColor='white', lineWidth=3, pos=(200, 0), closeShape=True)
pentagon_stim = visual.ShapeStim(win, vertices=make_polygon_vertices(60, 5), fillColor='cyan', lineColor='white', lineWidth=3, pos=(200, 0), closeShape=True)

SHAPE_STIMS = {
    'circle': circle_stim,
    'square': square_stim,
    'triangle': triangle_stim,
    'diamond': diamond_stim,
    'pentagon': pentagon_stim
}

shape_label = visual.TextStim(win, text='SHAPE', color='gray', height=24, pos=(200, 150))

# Divider line
divider = visual.Line(win, start=(0, -200), end=(0, 200), lineColor='gray', lineWidth=2)

# Text stimuli
instruction_text = visual.TextStim(win, text='', color='white', height=26, wrapWidth=1000)
rule_text = visual.TextStim(win, text='', color='yellow', height=22, pos=(0, -280), wrapWidth=1000)
progress_text = visual.TextStim(win, text='', color='gray', height=20, pos=(0, 320))

# Previous values display
prev_number_text = visual.TextStim(win, text='Prev: -', color='gray', height=18, pos=(-200, -120))
prev_shape_text = visual.TextStim(win, text='2-back: -', color='gray', height=18, pos=(200, -120))

# ---------------------
# 6. Helper Functions
# ---------------------
def draw_shape(shape_name):
    """Draw the specified shape"""
    SHAPE_STIMS[shape_name].draw()

# ---------------------
# 7. Show Instructions
# ---------------------
instructions = """
DUAL-TASK UPDATING GAME
========================

You will see TWO items on each trial:
    • LEFT: A NUMBER (0-9)
    • RIGHT: A SHAPE (circle, square, triangle, etc.)

FOLLOW TWO RULES SIMULTANEOUSLY:

RULE 1 (Numbers): Is the current number LARGER than the previous?
RULE 2 (Shapes): Does the current shape MATCH the shape from 2 trials ago?

YOUR RESPONSES:
    • Press 'N' if ONLY the number rule is met (number is larger)
    • Press 'S' if ONLY the shape rule is met (shape matches 2-back)
    • Press SPACEBAR if BOTH rules are met
    • Press ANY OTHER KEY if NEITHER rule is met

You must track BOTH streams in your memory!

Press SPACEBAR to begin...
"""

instruction_text.text = instructions
instruction_text.draw()
win.flip()
event.waitKeys(keyList=['space'])

# Practice reminder
practice_text = """
REMEMBER:
• Track if each number is LARGER than the previous
• Track if each shape MATCHES what you saw 2 trials ago

The first 2 trials won't have 2-back matches (no previous shapes to compare).

Press SPACEBAR to start...
"""
instruction_text.text = practice_text
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
# 8. Results storage
# ---------------------
results = []

# History tracking
prev_number = None
shape_history = []

# ---------------------
# 9. Trial Loop
# ---------------------
for trial_idx, trial in enumerate(stimuli):
    current_number = trial['number']
    current_shape = trial['shape']
    
    # Get current timestamp
    trial_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    # Determine correct responses
    # Rule 1: Number is larger than previous
    number_larger = prev_number is not None and current_number > prev_number
    
    # Rule 2: Shape matches 2-back
    shape_match = len(shape_history) >= N_BACK and current_shape == shape_history[-N_BACK]
    
    # Determine stimulus type (for analysis)
    # 0 = neither, 1 = number only, 2 = shape only, 3 = both
    if number_larger and shape_match:
        stimulus_type = 3  # Both - press spacebar
        correct_response = 'space'
    elif number_larger and not shape_match:
        stimulus_type = 1  # Number only - press 'n'
        correct_response = 'n'
    elif not number_larger and shape_match:
        stimulus_type = 2  # Shape only - press 's'
        correct_response = 's'
    else:
        stimulus_type = 0  # Neither - press other key
        correct_response = 'other'
    
    # Draw trial display
    progress_text.text = f"Trial {trial_idx + 1} of {TRIAL_NUMBER}"
    progress_text.draw()
    
    # Draw labels
    number_label.draw()
    shape_label.draw()
    divider.draw()
    
    # Draw number
    number_text.text = str(current_number)
    number_text.draw()
    
    # Draw shape
    draw_shape(current_shape)
    
    # Show previous values for reference
    if prev_number is not None:
        prev_number_text.text = f"Prev: {prev_number}"
    else:
        prev_number_text.text = "Prev: -"
    prev_number_text.draw()
    
    if len(shape_history) >= N_BACK:
        prev_shape_text.text = f"2-back: {shape_history[-N_BACK]}"
    else:
        prev_shape_text.text = "2-back: -"
    prev_shape_text.draw()
    
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
    if correct_response == 'space':
        response_correct = 1 if response == 'space' else 0
    elif correct_response == 'n':
        response_correct = 1 if response == 'n' else 0
    elif correct_response == 's':
        response_correct = 1 if response == 's' else 0
    else:  # 'other'
        response_correct = 1 if response not in ['space', 'n', 's'] else 0
    
    # Send marker: [stimulus_type, response_correct, reaction_time]
    if LSL_AVAILABLE and outlet:
        outlet.push_sample([stimulus_type, response_correct, rt])
    
    # Store result for CSV export
    results.append({
        'timestamp': trial_timestamp,
        'trial': trial_idx + 1,
        'number': current_number,
        'prev_number': prev_number if prev_number is not None else 'N/A',
        'shape': current_shape,
        'shape_2back': shape_history[-N_BACK] if len(shape_history) >= N_BACK else 'N/A',
        'number_larger': 1 if number_larger else 0,
        'shape_match': 1 if shape_match else 0,
        'stimulus_type': stimulus_type,
        'correct_response': correct_response,
        'response': response,
        'response_correct': response_correct,
        'rt': rt
    })
    
    # Update history
    prev_number = current_number
    shape_history.append(current_shape)
    
    core.wait(0.3)  # 300 ms ITI

win.close()

# ---------------------
# 10. Save results to CSV
# ---------------------
os.makedirs(os.path.join(SCRIPT_DIR, 'Results_CSV', 'Subject38'), exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = os.path.join(SCRIPT_DIR, 'Results_CSV', 'Subject38', f'dualTask_results_set3_{timestamp}.csv')

with open(filename, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['timestamp', 'trial', 'number', 'prev_number', 'shape', 
                                            'shape_2back', 'number_larger', 'shape_match', 'stimulus_type',
                                            'correct_response', 'response', 'response_correct', 'rt'])
    writer.writeheader()
    writer.writerows(results)

print(f"Dual-Task Updating Game finished. Results saved to {filename}. All markers sent to LSL.")

# ---------------------
# 11. Print summary statistics
# ---------------------
if results:
    total_correct = sum(1 for r in results if r['response_correct'] == 1)
    
    # Break down by trial type
    neither_trials = [r for r in results if r['stimulus_type'] == 0]
    number_trials = [r for r in results if r['stimulus_type'] == 1]
    shape_trials = [r for r in results if r['stimulus_type'] == 2]
    both_trials = [r for r in results if r['stimulus_type'] == 3]
    
    print("\n--- Summary Statistics ---")
    print(f"Overall Accuracy: {total_correct / len(results) * 100:.1f}%")
    
    if neither_trials:
        neither_correct = sum(1 for r in neither_trials if r['response_correct'] == 1)
        print(f"Neither rule met: {neither_correct / len(neither_trials) * 100:.1f}% ({len(neither_trials)} trials)")
    if number_trials:
        number_correct = sum(1 for r in number_trials if r['response_correct'] == 1)
        print(f"Number rule only: {number_correct / len(number_trials) * 100:.1f}% ({len(number_trials)} trials)")
    if shape_trials:
        shape_correct = sum(1 for r in shape_trials if r['response_correct'] == 1)
        print(f"Shape rule only: {shape_correct / len(shape_trials) * 100:.1f}% ({len(shape_trials)} trials)")
    if both_trials:
        both_correct = sum(1 for r in both_trials if r['response_correct'] == 1)
        print(f"Both rules met: {both_correct / len(both_trials) * 100:.1f}% ({len(both_trials)} trials)")
    
    correct_rts = [r['rt'] for r in results if r['response_correct'] == 1]
    if correct_rts:
        print(f"Mean RT (correct): {sum(correct_rts)/len(correct_rts)*1000:.0f} ms")
    
    # Dual-task cost analysis
    if number_trials and shape_trials and both_trials:
        single_task_rt = ([r['rt'] for r in number_trials + shape_trials if r['response_correct'] == 1])
        dual_task_rt = [r['rt'] for r in both_trials if r['response_correct'] == 1]
        if single_task_rt and dual_task_rt:
            single_mean = sum(single_task_rt) / len(single_task_rt)
            dual_mean = sum(dual_task_rt) / len(dual_task_rt)
            print(f"\nDual-task cost: {(dual_mean - single_mean) * 1000:.0f} ms slower when both rules apply")
