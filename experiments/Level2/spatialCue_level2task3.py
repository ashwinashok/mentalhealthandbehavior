"""
Spatial Cueing Reaction Game - Level 2 Task 3
==============================================
A cue (arrow) indicates a location on the screen.
After a short delay, a target shape appears either:
    - In the cued location (VALID trial) → Press SPACEBAR
    - In a different location (INVALID trial) → Press any other key

This task measures spatial attention and cue validity effects.
Based on Posner's spatial cueing paradigm.
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
# 2. Spatial Configuration
# ---------------------
# Possible target locations (left, right, up, down)
LOCATIONS = {
    'LEFT': (-300, 0),
    'RIGHT': (300, 0),
    'UP': (0, 200),
    'DOWN': (0, -200)
}

# Arrow rotation angles for each direction (pointing outward)
ARROW_ROTATIONS = {
    'LEFT': 180,
    'RIGHT': 0,
    'UP': 90,
    'DOWN': -90
}

# Cue validity (proportion of valid trials)
# Valid = 70%, Invalid = 30% (typical Posner task ratio)
VALID_PROBABILITY = 0.70

# Timing parameters (in seconds)
CUE_DURATION = 0.3  # How long the cue arrow is shown
SOA = 0.4  # Stimulus Onset Asynchrony (delay between cue and target)
TARGET_DURATION = None  # Target stays until response

# Create trial list - 100 trials
trial_number = 100
stimuli = []

for _ in range(trial_number):
    # Randomly select cued location
    cue_location = random.choice(list(LOCATIONS.keys()))
    
    # Determine if this is a valid or invalid trial
    is_valid = random.random() < VALID_PROBABILITY
    
    if is_valid:
        # Target appears in cued location
        target_location = cue_location
        correct = 1  # Go trial - press spacebar
    else:
        # Target appears in different location
        other_locations = [loc for loc in LOCATIONS.keys() if loc != cue_location]
        target_location = random.choice(other_locations)
        correct = 0  # No-go trial - press other key
    
    stimuli.append({
        'cue_location': cue_location,
        'target_location': target_location,
        'is_valid': is_valid,
        'correct': correct
    })

random.shuffle(stimuli)

# ---------------------
# 3. PsychoPy Setup - window and visual stimuli
# ---------------------
win = visual.Window([1200, 800], color='black', units='pix')

# Helper functions to create vertices for shapes (workaround for PsychoPy bug)
def make_circle_vertices(radius, n_points=32):
    angles = np.linspace(0, 2*np.pi, n_points, endpoint=False)
    return [(radius * np.cos(a), radius * np.sin(a)) for a in angles]

def make_rect_vertices(width, height):
    hw, hh = width/2, height/2
    return [(-hw, -hh), (-hw, hh), (hw, hh), (hw, -hh)]

def make_arrow_vertices(length=80, width=40):
    """Create arrow shape vertices pointing to the right (0 degrees)"""
    # Arrow pointing right: triangle head + rectangle body
    head_length = length * 0.4
    body_length = length * 0.6
    head_width = width
    body_width = width * 0.4
    
    # Vertices for arrow pointing RIGHT
    vertices = [
        # Arrow head (triangle)
        (length/2, 0),  # tip
        (length/2 - head_length, head_width/2),  # top of head
        (length/2 - head_length, body_width/2),  # top inner corner
        # Body
        (-length/2, body_width/2),  # top left
        (-length/2, -body_width/2),  # bottom left
        # Back to head
        (length/2 - head_length, -body_width/2),  # bottom inner corner
        (length/2 - head_length, -head_width/2),  # bottom of head
    ]
    return vertices

# Central fixation cross
fixation = visual.TextStim(win, text='+', color='white', height=50)

# Cue arrow - large bright red arrow shape
arrow = visual.ShapeStim(win, vertices=make_arrow_vertices(100, 50), 
                          fillColor='#FF3333', lineColor='white', lineWidth=2, 
                          closeShape=True)

# Target shape (circle) - use ShapeStim with explicit vertices
target = visual.ShapeStim(win, vertices=make_circle_vertices(40), fillColor='lime', lineColor='white', lineWidth=3, closeShape=True)

# Location markers (boxes showing possible target locations) - use ShapeStim
location_boxes = {}
for loc_name, pos in LOCATIONS.items():
    box = visual.ShapeStim(win, vertices=make_rect_vertices(100, 100), pos=pos, 
                           fillColor=None, lineColor='gray', lineWidth=2, closeShape=True)
    location_boxes[loc_name] = box

# Instructions text
instruction_text = visual.TextStim(win, text='', color='white', height=28, wrapWidth=1000)

# Feedback text
feedback_text = visual.TextStim(win, text='', color='white', height=24, pos=(0, -300))

# Trial type indicator
trial_type_text = visual.TextStim(win, text='', color='gray', height=20, pos=(0, 350))

# ---------------------
# 4. Helper function to draw location boxes
# ---------------------
def draw_location_boxes():
    """Draw the four location boxes"""
    for box in location_boxes.values():
        box.draw()

# ---------------------
# 5. Show Instructions
# ---------------------
instructions = """
SPATIAL CUEING REACTION GAME
=============================

A fixation cross (+) will appear in the center.
Then, an ARROW will point to one of 4 locations.
After a brief delay, a GREEN CIRCLE will appear.

YOUR TASK:
• Press SPACEBAR if the target appears WHERE THE ARROW POINTED
  (This is a VALID trial - arrow predicted correctly)

• Press ANY OTHER KEY if the target appears ELSEWHERE
  (This is an INVALID trial - arrow predicted incorrectly)

Pay attention to WHERE the arrow points!
The arrow usually (but not always) predicts correctly.

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
# 6. Results storage
# ---------------------
results = []

# ---------------------
# 7. Trial loop - Spatial Cueing Task
# ---------------------
for trial in stimuli:
    # Get current timestamp
    trial_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    cue_location = trial['cue_location']
    target_location = trial['target_location']
    is_valid = trial['is_valid']
    correct = trial['correct']
    
    # Phase 1: Fixation (500ms)
    draw_location_boxes()
    fixation.draw()
    win.flip()
    core.wait(0.5)
    
    # Phase 2: Cue presentation
    draw_location_boxes()
    fixation.draw()
    
    # Draw arrow pointing to cued location
    arrow.ori = ARROW_ROTATIONS[cue_location]
    arrow.draw()
    
    win.flip()
    core.wait(CUE_DURATION)
    
    # Phase 3: SOA delay (just fixation)
    draw_location_boxes()
    fixation.draw()
    win.flip()
    core.wait(SOA)
    
    # Phase 4: Target presentation
    draw_location_boxes()
    fixation.draw()
    
    # Draw target at specified location
    target.pos = LOCATIONS[target_location]
    target.draw()
    
    # Highlight the target box
    location_boxes[target_location].lineColor = 'lime'
    location_boxes[target_location].draw()
    
    win.flip()
    
    # Start timing for RT
    trial_clock = core.Clock()
    
    # Wait for key press
    keys = event.waitKeys()
    
    # Reset box color
    location_boxes[target_location].lineColor = 'gray'
    
    if 'escape' in keys:
        break
    
    response = keys[0]
    rt = trial_clock.getTime()
    
    # Clear screen immediately after response
    win.flip()
    
    # Determine if response is correct
    # For valid trials (correct=1): spacebar is correct
    # For invalid trials (correct=0): any key except spacebar is correct
    response_correct = 1 if (response == 'space' and correct == 1) or (response != 'space' and correct == 0) else 0
    
    # Send marker: [stimulus_type, response_correct, reaction_time]
    if LSL_AVAILABLE and outlet:
        outlet.push_sample([correct, response_correct, rt])
    
    # Store result for CSV export
    results.append({
        'timestamp': trial_timestamp,
        'stimulus': f"{cue_location}_{target_location}",
        'cue_location': cue_location,
        'target_location': target_location,
        'validity': 'valid' if is_valid else 'invalid',
        'stimulus_type': correct,
        'response': response,
        'response_correct': response_correct,
        'rt': rt
    })
    
    core.wait(0.3)  # 300 ms ITI (shorter for this task)

win.close()

# ---------------------
# 8. Save results to CSV
# ---------------------
# Create Results folder if it doesn't exist
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(SCRIPT_DIR, 'Results_CSV', 'Level2'), exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = os.path.join(SCRIPT_DIR, 'Results_CSV', 'Subject42', f'spatialCue_results_set4_{timestamp}.csv')

with open(filename, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['timestamp', 'stimulus', 'cue_location', 'target_location', 'validity', 
                                            'stimulus_type', 'response', 'response_correct', 'rt'])
    writer.writeheader()
    writer.writerows(results)

print(f"Spatial Cueing Task finished. Results saved to {filename}. All markers sent to LSL.")

# ---------------------
# 9. Print summary statistics
# ---------------------
if results:
    valid_trials = [r for r in results if r['validity'] == 'valid']
    invalid_trials = [r for r in results if r['validity'] == 'invalid']
    
    valid_correct = sum(1 for r in valid_trials if r['response_correct'] == 1)
    invalid_correct = sum(1 for r in invalid_trials if r['response_correct'] == 1)
    
    valid_rt = [r['rt'] for r in valid_trials if r['response_correct'] == 1]
    invalid_rt = [r['rt'] for r in invalid_trials if r['response_correct'] == 1]
    
    print("\n--- Summary Statistics ---")
    if valid_trials:
        print(f"Valid trials: {len(valid_trials)} ({valid_correct} correct, {valid_correct/len(valid_trials)*100:.1f}%)")
    else:
        print("Valid trials: 0")
    if invalid_trials:
        print(f"Invalid trials: {len(invalid_trials)} ({invalid_correct} correct, {invalid_correct/len(invalid_trials)*100:.1f}%)")
    else:
        print("Invalid trials: 0")
    if valid_rt:
        print(f"Mean RT (valid correct): {sum(valid_rt)/len(valid_rt)*1000:.0f} ms")
    if invalid_rt:
        print(f"Mean RT (invalid correct): {sum(invalid_rt)/len(invalid_rt)*1000:.0f} ms")
