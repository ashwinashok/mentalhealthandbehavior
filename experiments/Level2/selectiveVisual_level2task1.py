"""
Selective Visual Attention Task - Level 2 Task 1
=================================================
Screen shows animal shapes at a time.
Participants press SPACEBAR if it's a target (dog shape) 
and another key (any other key) for non-target images (wolf, fox, cat shapes).

Difficulty: Distractor shapes look similar to the target - requires more careful visual discrimination.
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
# 2. Stimuli Setup - Target vs Distractors
# ---------------------
# Target: Dog (press spacebar)
# Distractors: Wolf, Fox, Cat (press any other key)
# Using shapes with distinct characteristics to represent animals

TARGET_ANIMAL = 'DOG'
DISTRACTOR_ANIMALS = ['WOLF', 'FOX', 'CAT']

# Animal visual characteristics (simulated with shapes and colors)
# In a real experiment, you would use actual images
ANIMAL_CONFIG = {
    'DOG': {
        'shape': 'circle',
        'color': '#8B4513',  # Brown
        'size': 80,
        'ears': 'round',
        'label': 'DOG'
    },
    'WOLF': {
        'shape': 'circle', 
        'color': '#696969',  # Gray (similar to dog but darker)
        'size': 85,
        'ears': 'pointed',
        'label': 'WOLF'
    },
    'FOX': {
        'shape': 'circle',
        'color': '#D2691E',  # Orange-brown (similar to dog)
        'size': 75,
        'ears': 'pointed',
        'label': 'FOX'
    },
    'CAT': {
        'shape': 'circle',
        'color': '#A0522D',  # Sienna (similar to dog)
        'size': 70,
        'ears': 'pointed',
        'label': 'CAT'
    }
}

# Create trial list - 100 trials
trial_number = 100
all_animals = [TARGET_ANIMAL] + DISTRACTOR_ANIMALS
stimuli = []

for _ in range(trial_number):
    animal = random.choice(all_animals)
    if animal == TARGET_ANIMAL:
        stimuli.append((animal, 1))  # 1 = go (press spacebar for target)
    else:
        stimuli.append((animal, 0))  # 0 = no-go (press other key for distractors)

random.shuffle(stimuli)

# ---------------------
# 3. PsychoPy Setup - window and visual stimuli
# ---------------------
win = visual.Window([1200, 800], color='black', units='pix')

# Helper functions to create vertices for shapes (workaround for PsychoPy bug)
def make_circle_vertices(radius, n_points=32):
    angles = np.linspace(0, 2*np.pi, n_points, endpoint=False)
    return [(radius * np.cos(a), radius * np.sin(a)) for a in angles]

def make_polygon_vertices(radius, n_sides):
    angles = np.linspace(0, 2*np.pi, n_sides, endpoint=False) - np.pi/2
    return [(radius * np.cos(a), radius * np.sin(a)) for a in angles]

# Instructions text
instruction_text = visual.TextStim(win, text='', color='white', height=28, wrapWidth=1000)

# Animal body (main shape) - use ShapeStim with explicit vertices
body_shape = visual.ShapeStim(win, vertices=make_circle_vertices(80), fillColor='brown', lineColor='white', lineWidth=2, closeShape=True)

# Ear shapes (will be drawn based on animal type) - triangles for pointed ears
left_ear = visual.ShapeStim(win, vertices=make_polygon_vertices(25, 3), fillColor='brown', lineColor='white', closeShape=True)
right_ear = visual.ShapeStim(win, vertices=make_polygon_vertices(25, 3), fillColor='brown', lineColor='white', closeShape=True)

# Round ears for dog
left_ear_round = visual.ShapeStim(win, vertices=make_circle_vertices(20), fillColor='brown', lineColor='white', pos=(-50, 70), closeShape=True)
right_ear_round = visual.ShapeStim(win, vertices=make_circle_vertices(20), fillColor='brown', lineColor='white', pos=(50, 70), closeShape=True)

# Eyes
left_eye = visual.ShapeStim(win, vertices=make_circle_vertices(10), fillColor='white', lineColor='black', pos=(-25, 20), closeShape=True)
right_eye = visual.ShapeStim(win, vertices=make_circle_vertices(10), fillColor='white', lineColor='black', pos=(25, 20), closeShape=True)
left_pupil = visual.ShapeStim(win, vertices=make_circle_vertices(5), fillColor='black', lineColor='black', pos=(-25, 20), closeShape=True)
right_pupil = visual.ShapeStim(win, vertices=make_circle_vertices(5), fillColor='black', lineColor='black', pos=(25, 20), closeShape=True)

# Nose - triangle pointing down
nose = visual.ShapeStim(win, vertices=make_polygon_vertices(12, 3), fillColor='black', lineColor='black', pos=(0, -10), closeShape=True)
nose.ori = 180  # Point downward

# Label below the animal
label_text = visual.TextStim(win, text='', color='white', height=30, pos=(0, -150))

# ---------------------
# 4. Helper function to draw animal
# ---------------------
def draw_animal(animal_name, show_label=True):
    """Draw the animal shape based on configuration"""
    config = ANIMAL_CONFIG[animal_name]
    
    # Set body color and update vertices for size
    body_shape.fillColor = config['color']
    body_shape.vertices = make_circle_vertices(config['size'])
    body_shape.draw()
    
    # Draw ears based on type
    if config['ears'] == 'round':
        # Round ears (Dog)
        left_ear_round.fillColor = config['color']
        right_ear_round.fillColor = config['color']
        left_ear_round.pos = (-config['size']*0.6, config['size']*0.8)
        right_ear_round.pos = (config['size']*0.6, config['size']*0.8)
        left_ear_round.draw()
        right_ear_round.draw()
    else:
        # Pointed ears (Wolf, Fox, Cat)
        left_ear.fillColor = config['color']
        right_ear.fillColor = config['color']
        left_ear.pos = (-config['size']*0.5, config['size']*0.9)
        right_ear.pos = (config['size']*0.5, config['size']*0.9)
        left_ear.ori = 30
        right_ear.ori = -30
        left_ear.draw()
        right_ear.draw()
    
    # Draw eyes
    left_eye.pos = (-config['size']*0.3, config['size']*0.2)
    right_eye.pos = (config['size']*0.3, config['size']*0.2)
    left_pupil.pos = (-config['size']*0.3, config['size']*0.2)
    right_pupil.pos = (config['size']*0.3, config['size']*0.2)
    left_eye.draw()
    right_eye.draw()
    left_pupil.draw()
    right_pupil.draw()
    
    # Draw nose
    nose.pos = (0, -config['size']*0.15)
    nose.draw()
    
    # Draw label if requested
    if show_label:
        label_text.text = config['label']
        label_text.pos = (0, -config['size'] - 70)
        label_text.draw()

# ---------------------
# 5. Show Instructions
# ---------------------
instructions = """
SELECTIVE VISUAL ATTENTION TASK
================================

You will see animal faces appear on screen.

YOUR TASK:
• Press SPACEBAR when you see a DOG (round ears, brown)
• Press ANY OTHER KEY for other animals (Wolf, Fox, Cat)

The animals look similar - pay close attention to:
- Ear shape (round = dog, pointed = others)
- Exact color shade

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
# 7. Trial loop - Selective Visual Task
# ---------------------
for stim, correct in stimuli:
    # Get current timestamp
    trial_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    # Draw the animal (no label shown)
    draw_animal(stim, show_label=False)
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
    # For target (dog, correct=1): spacebar is correct
    # For distractors (correct=0): any key except spacebar is correct
    response_correct = 1 if (response == 'space' and correct == 1) or (response != 'space' and correct == 0) else 0
    
    # Send marker: [stimulus_type, response_correct, reaction_time]
    if LSL_AVAILABLE and outlet:
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
# 8. Save results to CSV
# ---------------------
# Create Results folder if it doesn't exist
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(SCRIPT_DIR, 'Results_CSV', 'Level2'), exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = os.path.join(SCRIPT_DIR, 'Results_CSV', 'Subject38', f'selectiveVisual_results_set3_{timestamp}.csv')

with open(filename, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['timestamp', 'stimulus', 'stimulus_type', 'response', 'response_correct', 'rt'])
    writer.writeheader()
    writer.writerows(results)

print(f"Selective Visual Task finished. Results saved to {filename}. All markers sent to LSL.")
