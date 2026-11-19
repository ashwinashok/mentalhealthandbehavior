"""
Color-Location Binding Memory Task - Level 3 Task 2
=====================================================
Phase 1 - Encoding:
    Screen shows multiple objects (3-5 shapes/icons), each with a specific color
    and specific position. The display stays for a few seconds and disappears.

Phase 2 - Test:
    Participants see either a single item or a full set and must decide:
    - Press SPACEBAR if the color AND location are SAME as before
    - Press ANY OTHER KEY if the color OR location has CHANGED

This task measures visual working memory and feature binding.
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
# Possible positions on screen (grid-like arrangement)
POSITIONS = [
    (-250, 150),   # top-left
    (0, 150),      # top-center
    (250, 150),    # top-right
    (-250, -50),   # middle-left
    (0, -50),      # middle-center
    (250, -50),    # middle-right
    (-250, -250),  # bottom-left
    (0, -250),     # bottom-center
    (250, -250),   # bottom-right
]

# Available colors
COLORS = {
    'RED': '#FF4444',
    'BLUE': '#4444FF',
    'GREEN': '#44DD44',
    'YELLOW': '#FFFF44',
    'PURPLE': '#AA44AA',
    'ORANGE': '#FF8844',
    'CYAN': '#44DDDD',
    'PINK': '#FF88AA'
}

# Available shapes
SHAPES = ['circle', 'square', 'triangle', 'diamond', 'star']

# Task parameters
NUM_OBJECTS_MIN = 3
NUM_OBJECTS_MAX = 5
ENCODING_DURATION = 4.0  # Seconds to show encoding display
RETENTION_INTERVAL = 1.0  # Blank screen between encoding and test
TRIAL_NUMBER = 50  # Total number of trials

# Change probability (proportion of trials where something changes)
CHANGE_PROBABILITY = 0.5

# ---------------------
# 4. PsychoPy Setup
# ---------------------
win = visual.Window([1200, 800], color='black', units='pix')

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

# Shape stimuli - use ShapeStim with explicit vertices to avoid PsychoPy bug
circle_stim = visual.ShapeStim(win, vertices=make_circle_vertices(40), fillColor='white', lineColor='white', lineWidth=3, closeShape=True)
square_stim = visual.ShapeStim(win, vertices=make_rect_vertices(70, 70), fillColor='white', lineColor='white', lineWidth=3, closeShape=True)
triangle_stim = visual.ShapeStim(win, vertices=make_polygon_vertices(45, 3), fillColor='white', lineColor='white', lineWidth=3, closeShape=True)
diamond_stim = visual.ShapeStim(win, vertices=make_polygon_vertices(45, 4), fillColor='white', lineColor='white', lineWidth=3, closeShape=True)
star_stim = visual.ShapeStim(win, vertices=make_polygon_vertices(45, 5), fillColor='white', lineColor='white', lineWidth=3, closeShape=True)

SHAPE_STIMS = {
    'circle': circle_stim,
    'square': square_stim,
    'triangle': triangle_stim,
    'diamond': diamond_stim,
    'star': star_stim
}

# Text stimuli
instruction_text = visual.TextStim(win, text='', color='white', height=28, wrapWidth=1000)
phase_text = visual.TextStim(win, text='', color='gray', height=24, pos=(0, 350))
prompt_text = visual.TextStim(win, text='', color='yellow', height=28, pos=(0, -320))
fixation = visual.TextStim(win, text='+', color='white', height=50)
progress_text = visual.TextStim(win, text='', color='gray', height=20, pos=(0, 320))

# Test indicator (highlights which item to check in single-probe mode)
probe_indicator = visual.ShapeStim(win, vertices=make_rect_vertices(110, 110), fillColor=None, lineColor='white', lineWidth=3, closeShape=True)

# ---------------------
# 5. Helper Functions
# ---------------------
def draw_shape(shape_name, position, color):
    """Draw a shape at the specified position with specified color"""
    stim = SHAPE_STIMS[shape_name]
    stim.pos = position
    stim.fillColor = color
    stim.lineColor = 'white'
    stim.draw()

def generate_display(num_objects):
    """Generate a random display of objects with unique positions and colors"""
    positions = random.sample(POSITIONS, num_objects)
    colors = random.sample(list(COLORS.values()), num_objects)
    shapes = random.choices(list(SHAPES), k=num_objects)
    
    objects = []
    for i in range(num_objects):
        objects.append({
            'shape': shapes[i],
            'position': positions[i],
            'color': colors[i]
        })
    return objects

def draw_display(objects, highlight_index=None):
    """Draw all objects in the display"""
    for i, obj in enumerate(objects):
        draw_shape(obj['shape'], obj['position'], obj['color'])
        if highlight_index == i:
            probe_indicator.pos = obj['position']
            probe_indicator.draw()

def create_changed_display(original_objects, change_type='color'):
    """Create a modified version of the display"""
    objects = [obj.copy() for obj in original_objects]
    change_idx = random.randint(0, len(objects) - 1)
    
    if change_type == 'color':
        # Change the color of one object
        current_colors = [obj['color'] for obj in objects]
        available_colors = [c for c in COLORS.values() if c not in current_colors]
        if available_colors:
            objects[change_idx]['color'] = random.choice(available_colors)
    elif change_type == 'location':
        # Change the position of one object
        current_positions = [obj['position'] for obj in objects]
        available_positions = [p for p in POSITIONS if p not in current_positions]
        if available_positions:
            objects[change_idx]['position'] = random.choice(available_positions)
    elif change_type == 'both':
        # Change both color and location
        current_colors = [obj['color'] for obj in objects]
        available_colors = [c for c in COLORS.values() if c not in current_colors]
        current_positions = [obj['position'] for obj in objects]
        available_positions = [p for p in POSITIONS if p not in current_positions]
        if available_colors:
            objects[change_idx]['color'] = random.choice(available_colors)
        if available_positions:
            objects[change_idx]['position'] = random.choice(available_positions)
    
    return objects, change_idx, change_type

# ---------------------
# 6. Create Trial List
# ---------------------
trials = []
for _ in range(TRIAL_NUMBER):
    num_objects = random.randint(NUM_OBJECTS_MIN, NUM_OBJECTS_MAX)
    is_change = random.random() < CHANGE_PROBABILITY
    
    if is_change:
        change_type = random.choice(['color', 'location', 'both'])
        correct = 0  # No-go (something changed)
    else:
        change_type = 'none'
        correct = 1  # Go (same as before)
    
    trials.append({
        'num_objects': num_objects,
        'is_change': is_change,
        'change_type': change_type,
        'correct': correct
    })

random.shuffle(trials)

# ---------------------
# 7. Show Instructions
# ---------------------
instructions = """
COLOR-LOCATION BINDING MEMORY TASK
===================================

In this task, you will see a set of colored shapes on screen.
Your job is to REMEMBER their colors AND positions.

After a brief delay, you will see the shapes again.

YOUR TASK:
• Press SPACEBAR if everything is the SAME
  (all colors and positions unchanged)

• Press ANY OTHER KEY if something CHANGED
  (a color moved OR a shape changed color)

Pay close attention to BOTH color AND location!

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
# 8. Results storage
# ---------------------
results = []

# ---------------------
# 9. Trial Loop
# ---------------------
for trial_idx, trial in enumerate(trials):
    num_objects = trial['num_objects']
    is_change = trial['is_change']
    change_type = trial['change_type']
    correct = trial['correct']
    
    # Get current timestamp
    trial_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    # Generate original display
    original_objects = generate_display(num_objects)
    
    # Phase 1: Fixation
    fixation.draw()
    win.flip()
    core.wait(0.5)
    
    # Phase 2: Encoding (show objects)
    phase_text.text = "REMEMBER these colors and positions"
    phase_text.draw()
    progress_text.text = f"Trial {trial_idx + 1} of {TRIAL_NUMBER}"
    progress_text.draw()
    draw_display(original_objects)
    win.flip()
    core.wait(ENCODING_DURATION)
    
    # Phase 3: Retention interval (blank screen)
    fixation.draw()
    win.flip()
    core.wait(RETENTION_INTERVAL)
    
    # Phase 4: Test display
    if is_change:
        test_objects, change_idx, actual_change = create_changed_display(original_objects, change_type)
    else:
        test_objects = original_objects
        change_idx = -1
        actual_change = 'none'
    
    phase_text.text = "SAME or CHANGED?"
    phase_text.draw()
    draw_display(test_objects)
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
    # For same trials (correct=1): spacebar is correct
    # For change trials (correct=0): any key except spacebar is correct
    response_correct = 1 if (response == 'space' and correct == 1) or (response != 'space' and correct == 0) else 0
    
    # Send marker: [stimulus_type, response_correct, reaction_time]
    if LSL_AVAILABLE and outlet:
        outlet.push_sample([correct, response_correct, rt])
    
    # Store result for CSV export
    results.append({
        'timestamp': trial_timestamp,
        'trial': trial_idx + 1,
        'num_objects': num_objects,
        'change_type': actual_change,
        'stimulus_type': correct,
        'response': response,
        'response_correct': response_correct,
        'rt': rt
    })
    
    core.wait(0.3)  # 300 ms ITI

win.close()

# ---------------------
# 10. Save results to CSV
# ---------------------
os.makedirs(os.path.join(SCRIPT_DIR, 'Results_CSV', 'Subject38'), exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = os.path.join(SCRIPT_DIR, 'Results_CSV', 'Subject38', f'colorLocation_results_set3_{timestamp}.csv')

with open(filename, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['timestamp', 'trial', 'num_objects', 'change_type', 
                                            'stimulus_type', 'response', 'response_correct', 'rt'])
    writer.writeheader()
    writer.writerows(results)

print(f"Color-Location Binding Task finished. Results saved to {filename}. All markers sent to LSL.")

# ---------------------
# 11. Print summary statistics
# ---------------------
if results:
    same_trials = [r for r in results if r['change_type'] == 'none']
    change_trials = [r for r in results if r['change_type'] != 'none']
    
    same_correct = sum(1 for r in same_trials if r['response_correct'] == 1)

    change_correct = sum(1 for r in change_trials if r['response_correct'] == 1)
    
    print("\n--- Summary Statistics ---")
    print(f"Overall Accuracy: {sum(1 for r in results if r['response_correct'] == 1) / len(results) * 100:.1f}%")
    if same_trials:
        print(f"'Same' trials accuracy: {same_correct / len(same_trials) * 100:.1f}% ({same_correct}/{len(same_trials)})")
    if change_trials:
        print(f"'Change' trials accuracy: {change_correct / len(change_trials) * 100:.1f}% ({change_correct}/{len(change_trials)})")
    
    # Break down by change type
    for ctype in ['color', 'location', 'both']:
        ctype_trials = [r for r in results if r['change_type'] == ctype]
        if ctype_trials:
            ctype_correct = sum(1 for r in ctype_trials if r['response_correct'] == 1)
            print(f"  {ctype.capitalize()} change detection: {ctype_correct / len(ctype_trials) * 100:.1f}%")
    
    correct_rts = [r['rt'] for r in results if r['response_correct'] == 1]
    if correct_rts:
        print(f"Mean RT (correct): {sum(correct_rts)/len(correct_rts)*1000:.0f} ms")
