#MONITOR = 'M16'
MONITOR = 'Surface'

if MONITOR == 'M16':
    SCREEN_SIZE = [2560, 1600]
    FRAME_RATE = 165
elif MONITOR == 'Surface':
    SCREEN_SIZE = [2880, 1920]
    FRAME_RATE = 60
else:
    SCREEN_SIZE == [2560, 1600]
    FRAME_RATE = 60

FRAME_RATE = 60
IS_TESTING = True
UNITS = 'height'
if IS_TESTING:
    DATA_DIR = 'test_data'
else:
    DATA_DIR = 'data'
PRACTICE_BLOCK_FILE = 'conditions/practice_block.csv'
BLOCKLIST_FILE = 'conditions/block_list.csv'
N_PRACTICE = 150
BLOCKS_PER_SESSION = 2

# Participant settings
DEFAULT_SUBJ = 0

# Stimulus settings
OUTPUT_COLS = 'key_resp,key_resp.rt'
STIM_SIZE = 7
STIM_DIST = 10
DOT_SIZE = 12 # in pixel. BEST: 0.1–0.3 degrees of visual angle 
DOT_SPEED = 0.2 # unit / frame. REC: 0.1-5 degrees per second
DOT_LIFE = 3 # in frames
N_DOTS = 100 # 5 ~ 50 per deg^2, 153 deg^2 => 2500 dots

# Participant settings

# Time Settings (in seconds)
FIX_TIME = 0.3
STIM_TIME = 0.25
ISI_TIME = 1.05 

# Eye tracker settings
USE_EYETRACKER = False
TRACKER = 'mouse'
#TRACKER = 'tobii'

# Trial settings
SKIP_INTRO = False
DO_PRACTICE = True
DO_TRIALS = True

# Text 
WELCOME_TEXT = "Welcome to the experiment!\n\n\n\n\n\n\n\nPress 'SPACE' to continue"
INS_TEXT = ["Target = 'UP'.\n\nPress the arrowkey ('left' or 'right' or no press) on the side where the target was presented.\n\n\n\n\n\nPress 'SPACE' to start"]
INS_TEXT_1 = ["Target = 'UP'.\n\nPress the arrowkey ('left' or 'right' or no press) on the side where the target was presented.\n\n\n\n\n\nPress 'SPACE' to start"]

# Special Modes (un-comment to turn it on)
# Only run practice, not trials
#DO_PRACTICE = True
#DO_TRIALS = False

# Override settings (un-comment if needed)
# DO_PRACTICE = False