"""
Picture Recall/Recognition Game - Level 3 Task 1
=================================================
The game works in BATCHES of 5 images:

BATCH 1:
  - Study Phase: Show images 1-5 (one at a time) - participants see "Picture 1", "Picture 2", etc.
  - Question Phase: Ask questions referring to "1st picture", "2nd picture", etc.
    (NO image shown - must recall from memory!)

BATCH 2:
  - Study Phase: Show images 6-10 (one at a time)
  - Question Phase: Ask questions about each picture by order

Images are randomly shuffled at the start. Participants don't see image filenames,
only the order (1st, 2nd, 3rd, etc.). The code internally tracks the mapping.

Questions and correct answers are loaded from questions_answers.csv

This task measures visual recognition memory and recall accuracy.
"""

from psychopy import visual, core, event
try:
    from pylsl import StreamOutlet, StreamInfo
    PYLSL_INSTALLED = True
except ImportError:
    print("pylsl not installed. LSL markers will be disabled.")
    PYLSL_INSTALLED = False
import csv
import random
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
PICTURES_FOLDER = os.path.join(SCRIPT_DIR, 'Pictures')
CSV_FILE = os.path.join(SCRIPT_DIR, 'questions_answers.csv')

# ---------------------
# 3. CONFIGURATION
# ---------------------
IMAGES_PER_BATCH = 5     # Number of images to study before questions
QUESTIONS_PER_IMAGE = 5  # Number of random questions to ask per image
STUDY_DURATION = 5.0     # Seconds to show each picture during study phase

# Ordinal labels for referring to images
ORDINAL_LABELS = ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', '10th',
                  '11th', '12th', '13th', '14th', '15th', '16th', '17th', '18th', '19th', '20th']

# ---------------------
# 4. Load questions and answers from CSV
# ---------------------
def load_questions_and_answers(csv_path):
    """
    Load questions and answers from CSV file.
    
    CSV Format:
    - First row: image, Question1, Question2, Question3, ...
    - Following rows: ImageName.png, 0, 1, 1, 0, ...
    
    Returns:
        questions: list of question strings
        answers: dict mapping image_name -> list of answers (0 or 1)
    """
    questions = []
    answers = {}
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        # First row contains headers (image name column + questions)
        headers = next(reader)
        questions = headers[1:]  # All columns except first are questions
        
        # Following rows contain image name + answers
        for row in reader:
            if len(row) > 1:
                image_name = row[0].strip()
                image_answers = [int(a.strip()) for a in row[1:]]
                answers[image_name] = image_answers
    
    return questions, answers

# Load from CSV
if os.path.exists(CSV_FILE):
    ALL_QUESTIONS, ANSWERS_BY_IMAGE = load_questions_and_answers(CSV_FILE)
    print(f"Loaded {len(ALL_QUESTIONS)} questions from CSV")
    print(f"Loaded answers for {len(ANSWERS_BY_IMAGE)} images")
else:
    print(f"ERROR: CSV file not found: {CSV_FILE}")
    print("Please create questions_answers.csv with your questions and answers.")
    exit()

# Get list of images from the CSV (in order they appear)
IMAGES = list(ANSWERS_BY_IMAGE.keys())

# ---------------------
# 5. Helper function to check if image exists
# ---------------------
def get_image_path(image_name):
    """Get full path to image, checking multiple extensions"""
    base_name = os.path.splitext(image_name)[0]
    extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif']
    
    # First try the exact name
    full_path = os.path.join(PICTURES_FOLDER, image_name)
    if os.path.exists(full_path):
        return full_path
    
    # Try other extensions
    for ext in extensions:
        full_path = os.path.join(PICTURES_FOLDER, base_name + ext)
        if os.path.exists(full_path):
            return full_path
    
    return None

# ---------------------
# 6. Validate images exist
# ---------------------
valid_images = []
for img_name in IMAGES:
    img_path = get_image_path(img_name)
    if img_path:
        valid_images.append((img_name, img_path))
    else:
        print(f"WARNING: Image not found: {img_name}")

if len(valid_images) == 0:
    print(f"ERROR: No images found in {PICTURES_FOLDER}")
    print("Please add images that match the names in your CSV file.")
    exit()

print(f"Found {len(valid_images)} images to study")

# ---------------------
# 7. SHUFFLE IMAGES RANDOMLY
# ---------------------
random.shuffle(valid_images)
print("Images have been randomly shuffled for this session")

# Create a mapping of presentation order to actual image
# This allows us to refer to images by order (1st, 2nd, etc.) while tracking the real image
image_order_mapping = {}
for idx, (img_name, img_path) in enumerate(valid_images):
    image_order_mapping[idx] = {
        'order': idx + 1,
        'ordinal': ORDINAL_LABELS[idx] if idx < len(ORDINAL_LABELS) else f"{idx+1}th",
        'image_name': img_name,
        'image_path': img_path
    }

# Calculate number of batches
num_batches = (len(valid_images) + IMAGES_PER_BATCH - 1) // IMAGES_PER_BATCH
print(f"Will run {num_batches} batch(es) of up to {IMAGES_PER_BATCH} images each")

# ---------------------
# 8. PsychoPy Setup - window and visual stimuli
# ---------------------
win = visual.Window([1200, 800], color='black', units='pix')

# Image stimulus
image_stim = visual.ImageStim(win, image=None, size=(700, 525), pos=(0, 0))

# Text stimuli
instruction_text = visual.TextStim(win, text='', color='white', height=28, wrapWidth=1000)
question_text = visual.TextStim(win, text='', color='yellow', height=34, pos=(0, 50), wrapWidth=1000)
image_label = visual.TextStim(win, text='', color='cyan', height=40, pos=(0, 200), bold=True)
options_text = visual.TextStim(win, text='', color='white', height=28, pos=(0, -100), wrapWidth=1000)
phase_indicator = visual.TextStim(win, text='', color='gray', height=24, pos=(0, 350))
progress_text = visual.TextStim(win, text='', color='gray', height=20, pos=(0, 320))
batch_text = visual.TextStim(win, text='', color='orange', height=26, pos=(0, 280))
picture_number_text = visual.TextStim(win, text='', color='white', height=36, pos=(0, -320), bold=True)

# ---------------------
# 9. Show Instructions
# ---------------------
instructions_study = f"""
PICTURE RECALL/RECOGNITION GAME
================================

This task tests your visual memory.

HOW IT WORKS:
• You will see {IMAGES_PER_BATCH} pictures, one at a time
• Each picture will be labeled as "Picture 1", "Picture 2", etc.
• Try to REMEMBER the ORDER of the pictures!
• Then you will answer {QUESTIONS_PER_IMAGE} YES/NO questions about EACH picture
  (The picture will NOT be shown - you must recall from memory!)
  Questions will refer to "1st picture", "2nd picture", etc.

• Press SPACEBAR for YES
• Press ANY OTHER KEY for NO

The task has {num_batches} round(s) of {IMAGES_PER_BATCH} pictures each.

Press SPACEBAR to begin...
"""

instruction_text.text = instructions_study
instruction_text.draw()
win.flip()
event.waitKeys(keyList=['space'])

# ---------------------
# 10. Results storage
# ---------------------
results = []
total_correct = 0
total_questions = 0

# ---------------------
# 11. MAIN LOOP - Process images in batches
# ---------------------
for batch_num in range(num_batches):
    # Get images for this batch
    start_idx = batch_num * IMAGES_PER_BATCH
    end_idx = min(start_idx + IMAGES_PER_BATCH, len(valid_images))
    batch_images = valid_images[start_idx:end_idx]
    
    # Calculate the starting picture number for this batch
    batch_start_number = start_idx + 1
    
    # =====================
    # STUDY PHASE for this batch
    # =====================
    
    # Show batch intro
    instruction_text.text = f"""
BATCH {batch_num + 1} of {num_batches}

STUDY PHASE
-----------
You will now see {len(batch_images)} pictures.
They will be labeled Picture {batch_start_number} through Picture {start_idx + len(batch_images)}.

Look carefully and try to remember each one!
Each picture will be shown for {STUDY_DURATION:.0f} seconds.

Press SPACEBAR to start studying...
"""
    instruction_text.draw()
    win.flip()
    event.waitKeys(keyList=['space'])
    
    # Countdown
    for i in [3, 2, 1]:
        instruction_text.text = f"Get ready... {i}"
        instruction_text.draw()
        win.flip()
        core.wait(1.0)
    
    # Show each image in this batch
    phase_indicator.text = f"STUDY PHASE - Batch {batch_num + 1}"
    
    for idx, (img_name, img_path) in enumerate(batch_images):
        global_idx = start_idx + idx  # Global index across all images
        picture_num = global_idx + 1  # 1-based picture number
        
        phase_indicator.draw()
        progress_text.text = f"Picture {idx + 1} of {len(batch_images)} in this batch"
        progress_text.draw()
        batch_text.text = f"Batch {batch_num + 1}/{num_batches}"
        batch_text.draw()
        
        # Show picture number label (NOT the image filename!)
        picture_number_text.text = f"Picture {picture_num}"
        picture_number_text.draw()
        
        # Display the image
        image_stim.image = img_path
        image_stim.draw()
        
        win.flip()
        core.wait(STUDY_DURATION)
        
        # Brief blank between pictures
        win.flip()
        core.wait(0.5)
    
    # =====================
    # QUESTION PHASE for this batch
    # =====================
    
    # Transition message
    instruction_text.text = f"""
STUDY PHASE COMPLETE for Batch {batch_num + 1}!

Now comes the QUESTION PHASE.
You will answer {QUESTIONS_PER_IMAGE} questions about EACH picture.

IMPORTANT: The pictures will NOT be shown!
You must answer from MEMORY.
Questions will refer to pictures by their order (1st, 2nd, 3rd, etc.)

Press SPACEBAR for YES
Press ANY OTHER KEY for NO

Press SPACEBAR to begin questions...
"""
    instruction_text.draw()
    win.flip()
    event.waitKeys(keyList=['space'])
    
    phase_indicator.text = f"QUESTION PHASE - Batch {batch_num + 1} (From Memory!)"
    
    # Ask questions for each image in this batch
    for idx, (img_name, img_path) in enumerate(batch_images):
        global_idx = start_idx + idx  # Global index across all images
        picture_num = global_idx + 1  # 1-based picture number
        ordinal_label = ORDINAL_LABELS[global_idx] if global_idx < len(ORDINAL_LABELS) else f"{picture_num}th"
        
        # Get all answers for this image (using the actual image name internally)
        image_answers = ANSWERS_BY_IMAGE.get(img_name, [0] * len(ALL_QUESTIONS))
        
        # Randomly select which questions to ask (indices)
        num_questions = min(QUESTIONS_PER_IMAGE, len(ALL_QUESTIONS))
        selected_question_indices = random.sample(range(len(ALL_QUESTIONS)), num_questions)
        
        for q_num, q_idx in enumerate(selected_question_indices):
            question = ALL_QUESTIONS[q_idx]
            correct_answer = image_answers[q_idx] if q_idx < len(image_answers) else 0
            
            # Get current timestamp
            trial_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            
            # Draw phase indicator and progress (NO IMAGE!)
            phase_indicator.draw()
            progress_text.text = f"Picture {idx + 1}/{len(batch_images)} | Question {q_num + 1}/{num_questions}"
            progress_text.draw()
            batch_text.text = f"Batch {batch_num + 1}/{num_batches}"
            batch_text.draw()
            
            # Show which image we're asking about (by ORDER, not by filename!)
            image_label.text = f"About the {ordinal_label} picture (Picture {picture_num}):"
            image_label.draw()
            
            # Draw question
            question_text.text = question
            question_text.draw()
            
            win.flip()
            
            # Start timing for RT
            trial_clock = core.Clock()
            
            # Wait for response (any key)
            keys = event.waitKeys()
            
            if 'escape' in keys:
                break
            
            # SPACEBAR = YES (1), any other key = NO (0)
            response = 1 if keys[0] == 'space' else 0
            rt = trial_clock.getTime()
            
            # Check if correct
            is_correct = 1 if response == correct_answer else 0
            total_correct += is_correct
            total_questions += 1
            
            # Send marker: [question_index, response_correct, reaction_time]
            if LSL_AVAILABLE and outlet:
                outlet.push_sample([q_idx + 1, is_correct, rt])
            
            # Store result (includes both the order label and actual image name for analysis)
            results.append({
                'timestamp': trial_timestamp,
                'batch': batch_num + 1,
                'picture_order': picture_num,
                'ordinal_label': ordinal_label,
                'image_name': img_name,  # Internal tracking - actual image filename
                'question_index': q_idx + 1,
                'question': question,
                'response': 'YES' if response == 1 else 'NO',
                'correct_answer': 'YES' if correct_answer == 1 else 'NO',
                'is_correct': is_correct,
                'rt': rt
            })
            
            core.wait(0.2)  # Brief pause between questions
        
        if 'escape' in keys:
            break
    
    if 'escape' in keys:
        break
    
    # Brief pause between batches (if not the last batch)
    if batch_num < num_batches - 1:
        instruction_text.text = f"""
Batch {batch_num + 1} complete!

Take a short break if needed.

Press SPACEBAR to continue to Batch {batch_num + 2}...
"""
        instruction_text.draw()
        win.flip()
        event.waitKeys(keyList=['space'])

# ---------------------
# 12. Show Final Score
# ---------------------
if total_questions > 0:
    accuracy = (total_correct / total_questions) * 100
    final_message = f"""
TASK COMPLETE!

Your Score: {total_correct} / {total_questions} correct
Accuracy: {accuracy:.1f}%

Thank you for participating!

Press SPACEBAR to exit...
"""
else:
    final_message = """
TASK COMPLETE!

Thank you for participating!

Press SPACEBAR to exit...
"""

instruction_text.text = final_message
instruction_text.draw()
win.flip()
event.waitKeys(keyList=['space'])

win.close()

# ---------------------
# 13. Save results to CSV
# ---------------------
os.makedirs(os.path.join(SCRIPT_DIR, 'Results_CSV', 'Subject0'), exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = os.path.join(SCRIPT_DIR, 'Results_CSV', 'Subject42', f'pictureRecall_results_set4_{timestamp}.csv')

with open(filename, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['timestamp', 'batch', 'picture_order', 'ordinal_label', 
                                            'image_name', 'question_index', 'question', 
                                            'response', 'correct_answer', 'is_correct', 'rt'])
    writer.writeheader()
    writer.writerows(results)

print(f"Picture Recall Task finished. Results saved to {filename}.")

# ---------------------
# 14. Print summary statistics
# ---------------------
if results:
    print("\n--- Summary Statistics ---")
    print(f"Total Questions: {total_questions}")
    print(f"Correct Answers: {total_correct}")
    print(f"Accuracy: {(total_correct/total_questions)*100:.1f}%")
    
    # Per-batch breakdown
    print("\nPer-Batch Breakdown:")
    for b in range(1, num_batches + 1):
        batch_results = [r for r in results if r['batch'] == b]
        if batch_results:
            batch_correct = sum(r['is_correct'] for r in batch_results)
            print(f"  Batch {b}: {batch_correct}/{len(batch_results)} correct ({batch_correct/len(batch_results)*100:.1f}%)")
    
    # Per-picture breakdown (by order)
    print("\nPer-Picture Breakdown (by presentation order):")
    for order in range(1, len(valid_images) + 1):
        pic_results = [r for r in results if r['picture_order'] == order]
        if pic_results:
            pic_correct = sum(r['is_correct'] for r in pic_results)
            ordinal = ORDINAL_LABELS[order-1] if order-1 < len(ORDINAL_LABELS) else f"{order}th"
            actual_image = pic_results[0]['image_name']
            print(f"  Picture {order} ({ordinal}) [{actual_image}]: {pic_correct}/{len(pic_results)} correct")
    
    # Average RT
    correct_rts = [r['rt'] for r in results if r['is_correct'] == 1]
    if correct_rts:
        print(f"\nMean RT (correct): {sum(correct_rts)/len(correct_rts)*1000:.0f} ms")

# ---------------------
# 15. Save image order mapping for reference
# ---------------------
mapping_filename = os.path.join(SCRIPT_DIR, 'Results_CSV', 'Level3', f'pictureRecall_image_mapping_{timestamp}_set1.csv')
with open(mapping_filename, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['picture_order', 'ordinal_label', 'image_name'])
    writer.writeheader()
    for idx in range(len(valid_images)):
        writer.writerow({
            'picture_order': idx + 1,
            'ordinal_label': ORDINAL_LABELS[idx] if idx < len(ORDINAL_LABELS) else f"{idx+1}th",
            'image_name': valid_images[idx][0]
        })
print(f"Image order mapping saved to {mapping_filename}")
