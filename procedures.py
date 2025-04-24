# import libraries
from psychopy import core, monitors, visual, sound, gui, data, event, logging
from psychopy.tools.filetools import fromFile, toFile
from psychopy.hardware import keyboard
from psychopy import iohub
from psychopy.iohub import launchHubServer
from psychopy.iohub.client import ioHubConnection
from psychopy.iohub.util import hideWindow, showWindow
from psychopy.iohub.client.eyetracker.validation import TargetStim
import random, os, csv
import pandas as pd
import numpy as np
import pyxid2 as pyxid
from math import floor
# import modules
import params

# Define the function to send triggers to serial port
def send_triggers(device, value):
    """send value as hardware trigger"""
    device.activate_line(bitmask=value)

def setup_eeg():
    devices = pyxid.get_xid_devices()
    if not devices:
        print("No XID devices found")
        core.quit()
    dev = devices[0]
    print("Uding ", dev)
    
    dev.set_pulse_duration(5)
    
    return dev

def initialise_exp():
    """
    initialise experiment parameters, display a dialogue to input the
    participant information and create the data file
    """
    expInfo = {'subject': params.DEFAULT_SUBJ, 'session': '001'}
    expInfo['dateStr'] = data.getDateStr()
    # present a dialogue to change participant params
    dlg = gui.DlgFromDict(expInfo, title='attention', fixed=['dateStr'])

    if not dlg.OK:
        core.quit()
    
    # make a csv data file
    curr_dir = os.getcwd()
    
    data_dir = os.path.join(curr_dir, params.DATA_DIR)
    # make data directory if not exists
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    filename = str(expInfo['subject']) + '_' + expInfo['dateStr'] + '.csv'
    filename = os.path.join(data_dir, filename)
    open(filename, 'a').close()
    
    # set logging to console
    logging.console.setLevel(logging.getLevel('warning'))
    return filename

def setup_window():
    """set up the window"""
    mon = monitors.Monitor(params.MONITOR)
    win = visual.Window(size=params.SCREEN_SIZE, fullscr=True, screen=1,
        monitor=mon, units=params.UNITS)
    if params.FRAME_RATE == None:
        params.FRAME_RATE = win.getActualFrameRate(infoMsg='')
#    win.setMouseVisible(False)
    win.hideMessage()
    return win
        
def calibrate_eyetracker(win):
    """eyetracker calibration"""
    kb = keyboard.Keyboard()
    
    # instruction screen
    instruction_msg = visual.TextStim(win=win, pos=[0,0], height=0.05,
        text="Before starting the experiment, we need to calibrate the eye-tracker. During the calibration, please do not move your head and follow the dot on the screen with your eyes.\n\n\n\n\n\n\n\nPress 'SPACE' to start")
    instruction_msg.draw()
    win.flip()
    keys = kb.waitKeys(keyList=['space', 'escape'])
    if 'escape' in keys:
        core.quit()
    kb.clearEvents()
    
    # loading screen
    loading_msg = visual.TextStim(win=win, pos=[0,0], height=0.05,
        text="Preparing calibration. Please wait....")
    loading_msg.draw()
    win.flip()

    keys = kb.getKeys(keyList=['escape'])
    if 'escape' in keys:
        core.quit()
    kb.clearEvents()
    
    eyetracker_config = dict(name='tracker')
    devices_config = {}
    if params.TRACKER == 'mouse':
        devices_config['eyetracker.hw.mouse.EyeTracker'] = eyetracker_config
        eyetracker_config['calibration'] = dict(auto_pace=True,
                                            target_duration=1.5,
                                            target_delay=1.0,
                                            screen_background_color=(0, 0, 0),
                                            type='FIVE_POINTS',
                                            unit_type=None,
                                            color_type=None,
                                            target_attributes=dict(outer_diameter=0.05,
                                                                   inner_diameter=0.025,
                                                                   outer_fill_color=[-0.5, -0.5, -0.5],
                                                                   inner_fill_color=[-1, 1, -1],
                                                                   outer_line_color=[1, 1, 1],
                                                                   inner_line_color=[-1, -1, -1],
                                                                   animate=dict(enable=True,
                                                                                expansion_ratio=1.5,
                                                                                contract_only=False)
                                                                   )
                                            )
    elif params.TRACKER == 'tobii':
        eyetracker_config['calibration'] = dict(auto_pace=True,
                                            target_duration=1.5,
                                            target_delay=1.0,
                                            screen_background_color=(0, 0, 0),
                                            type='FIVE_POINTS',
                                            unit_type=None,
                                            color_type=None,
                                            target_attributes=dict(outer_diameter=0.05,
                                                                   inner_diameter=0.025,
                                                                   outer_fill_color=[-0.5, -0.5, -0.5],
                                                                   inner_fill_color=[-1, 1, -1],
                                                                   outer_line_color=[1, 1, 1],
                                                                   inner_line_color=[-1, -1, -1],
                                                                   animate=dict(enable=True,
                                                                                expansion_ratio=1.5,
                                                                                contract_only=False)
                                                                   )
                                            )
        devices_config['eyetracker.hw.tobii.EyeTracker'] = eyetracker_config
    else:
        print("{} is not a valid TRACKER name; please use 'mouse' or 'tobii'.".format(params.TRACKER))
        core.quit()
    
    io_hub_server = launchHubServer(window=win, **devices_config)
    eye_tracker = io_hub_server.getDevice('tracker')

    # Minimize the PsychoPy window if needed
    hideWindow(win)
    # Display calibration gfx window and run calibration.
    result = eye_tracker.runSetupProcedure()
    print("Calibration returned: ", result)
    # Maximize the PsychoPy window if needed
    showWindow(win)
    
#    kb = keyboard.Keyboard()
#    displayed_msg = visual.TextStim(win=win, pos=[0,0], height=0.05,
#        text="Now we need to validate the calibration results. Press 'SPACE' to start")
#    displayed_msg.draw()
#    win.flip()
#
#    keys = kb.waitKeys(maxWait=float('inf'), keyList=['space', 'escape'])
#    if 'escape' in keys:
#        core.quit()
#    kb.clearEvents()

def validate_eyetracker(win):
    """eyetracker validation"""
    target_stim = TargetStim(win, radius=0.025, fillcolor=[.5, .5, .5], edgecolor=[-1, -1, -1], edgewidth=2,
        dotcolor=[1, -1, -1], dotradius=0.005, units='height', colorspace='rgb')

    target_positions = 'FIVE_POINTS'

    validation_proc = iohub.ValidationProcedure(win,
        target=target_stim,  # target stim
        positions=target_positions,  # string constant or list of points
        randomize_positions=True,  # boolean
        expand_scale=1.5,  # float
        target_duration=1.5,  # float
        target_delay=1.0,  # float
        enable_position_animation=True,
        color_space='rgb',
        unit_type='height',
        progress_on_key="",  # str or None
        gaze_cursor=(-1.0, 1.0, -1.0),  # None or color value
        show_results_screen=True,  # bool
        save_results_screen=False,  # bool, only used if show_results_screen == True
        )

    validation_proc.run()
    if validation_proc.results:
        results = validation_proc.results
        print("++++ Validation Results ++++")
        print("Passed:", results['passed'])
        print("failed_pos_count:", results['positions_failed_processing'])
        print("Units:", results['reporting_unit_type'])
        print("min_error:", results['min_error'])
        print("max_error:", results['max_error'])
        print("mean_error:", results['mean_error'])
    else:
        print("Validation Aborted by User.")
        
    kb = keyboard.Keyboard()
    displayed_msg = visual.TextStim(win=win, pos=[0,0], height=0.05,
        text="If satisfied with the validation results, press 'SPACE' to continue.\n\nAlternatively, press 'R' to re-calibrate")
    displayed_msg.draw()
    win.flip()

    keys = kb.waitKeys(maxWait=float('inf'), keyList=['space', 'escape', 'r'])
    if 'escape' in keys:
        core.quit()
    elif 'r' in keys:
        calibrate_eyetracker(win)
        validate_eyetracker(win)
    kb.clearEvents()

def read_block_cond(blocklist_file=params.BLOCKLIST_FILE):
    df_blocklist = pd.read_csv(blocklist_file)
    return df_blocklist['block_name'].to_list()

def read_trial_cond(trial_cond):
    df_trial_cond = pd.read_csv(trial_cond)
    return df_trial_cond

def prepare_stimulus(win):
    components = {}
    fixation_pt = visual.ImageStim(win=win, name='fixation_pt', units='deg', 
        image='assets/fixation_pt.png', anchor='center', pos=(0, 0), size=[params.FIX_SIZE],
        color=[1,1,1], colorSpace='rgb', opacity=None, texRes=128.0,
        interpolate=True, depth=-4.0)
        
    fixation_region = visual.Circle(win, lineColor='black', radius=0.1, units='height')
    
    alert = sound.Sound('A', stereo=True)
    
    stim_left = visual.DotStim(win=win, name='stim_left', units='deg',
        nDots=params.N_DOTS, coherence=1, fieldPos=(-params.STIM_DIST, 0),
        fieldSize=params.STIM_SIZE, fieldShape='circle', dotSize=params.DOT_SIZE,
        dotLife=params.DOT_LIFE, dir=90, speed=params.DOT_SPEED)
        
    stim_right = visual.DotStim(win=win, name='stim_right', units='deg',
        nDots=params.N_DOTS, coherence=1, fieldPos=(params.STIM_DIST, 0),
        fieldSize=params.STIM_SIZE, fieldShape='circle', dotSize=params.DOT_SIZE,
        dotLife=params.DOT_LIFE, dir=90, speed=params.DOT_SPEED)
        
    components['fixation_pt'] = fixation_pt
    components['fixation_region'] = fixation_region
    components['alert'] = alert
    components['stim_left'] = stim_left
    components['stim_right'] = stim_right
    return components
    
def update_stims(components, condition):
    components['stim_left'].coherence = condition.coherence_left
    components['stim_left'].dir = condition.ori_left
        
    components['stim_right'].coherence = condition.coherence_right
    components['stim_right'].dir = condition.ori_right

def display_end_of_easy_practice(win, redo, accuracy):
    """display end of block information"""
    kb = keyboard.Keyboard()
    override = False # allows the experimenter to overwrite redo practice
    
    if redo:
        displayed_msg = visual.TextStim(win=win, pos=[0,0], height=0.05,
        text="It was close!!\nYour accuracy was: " + str(round(accuracy,2)) + "\n\nYou can re-attempt the practice.\n\n\n\n\nPress 'Space' to start")
    else:
        displayed_msg = visual.TextStim(win=win, pos=[0,0], height=0.05,
        text="Good job!!\nYour accuracy was: " + str(round(accuracy,2)) + "\n\n\n\n\nPress 'Space' to continue")
    displayed_msg.draw()
    win.flip()
    
    keys = kb.waitKeys(maxWait=float('inf'), keyList=['space', 's', 'escape'])
    if 'escape' in keys:
        core.quit()
    elif 's' in keys:
        override = True
    kb.clearEvents()
    
    return override
    
def display_end_of_practice(win, redo, accuracy):
    """display end of block information"""
    kb = keyboard.Keyboard()
    
    if redo:
        displayed_msg = visual.TextStim(win=win, pos=[0,0], height=0.05,
        text="It was close!!\nYour accuracy was: " + str(round(accuracy,2)) + "\n\nYou can re-attempt the practice and it will start with the highest difficulty and speed\n\n\n\n\nPress 'Space' to start")
    else:
        displayed_msg = visual.TextStim(win=win, pos=[0,0], height=0.05,
        text="Good job!!\nYour accuracy was: " + str(round(accuracy,2)) + "\n\n\n\n\nPress 'Space' to start the experiment")
    displayed_msg.draw()
    win.flip()
    
    keys = kb.waitKeys(maxWait=float('inf'), keyList=['space', 'escape'])
    if 'escape' in keys:
        core.quit()
    kb.clearEvents()
    
def display_end_of_block(win, block_n):
    """display end of block information"""
    kb = keyboard.Keyboard()
    
    displayed_msg = visual.TextStim(win=win, pos=[0,0], height=0.05,
        text="End of block " + str(block_n) + "\n\n\n\n\nPress 'Space' to start the next block")
    displayed_msg.draw()
    win.flip()
    
    keys = kb.waitKeys(maxWait=float('inf'), keyList=['space', 'escape'])
    if 'escape' in keys:
        core.quit()
    kb.clearEvents()

def display_end_of_session(win):
    """display end of block information"""
    kb = keyboard.Keyboard()
    
    displayed_msg = visual.TextStim(win=win, pos=[0,0], height=0.05,
        text="End of session.\n\nYou can take a longer rest before starting the next session\n\n\n\nPress 'Space' to start the next session")
    displayed_msg.draw()
    win.flip()
    
    keys = kb.waitKeys(maxWait=float('inf'), keyList=['space', 'escape'])
    if 'escape' in keys:
        core.quit()
    kb.clearEvents()

def run_intro(win):
    """display introduction and instructions"""
    kb = keyboard.Keyboard()
    components = prepare_stimulus(win)
    
    displayed_msg = visual.TextStim(win=win, pos=[0,0], height=0.05, wrapWidth=1.5,
        text=params.WELCOME_TEXT)
    displayed_msg.draw()
    win.flip()

    keys = kb.waitKeys(maxWait=float('inf'), keyList=['space', 'escape'])
    if 'escape' in keys:
        core.quit()
    kb.clearEvents()
    
    # page 1
    displayed_msg.text = ("Throughout the experiment, you need to fixate your "
        "eyes on the center of the screen, where you'll see a symbol as below: "
        "\n\n\n\n\n\n\nIf you move your eyes away from the center, you will hear "
        "a beep from the speakers to remind you to re-fixate.\n\nPress 'SPACE' "
        "to continue.")
    
    displayed_msg.draw()
    components['fixation_pt'].draw()
    win.flip()
    
    keys = kb.waitKeys(maxWait=float('inf'), keyList=['space', 'escape'])
    if 'escape' in keys:
        core.quit()
    kb.clearEvents()
    
    # page 2
    displayed_msg.text = ("During the experiment, you will see two circle areas "
        "on each side of the screen with many dots moving in random directions, "
        "as displayed below:\n\n\n\n\n\n\n\n\nPress 'SPACE' to conitnue.")
    
    components['stim_left'].coherence = 0
    components['stim_right'].coherence = 0
    
    while True:
        displayed_msg.draw()
        components['stim_left'].draw()
        components['stim_right'].draw()
        win.flip()
        
        keys = kb.getKeys(keyList=['space', 'escape'])
        if 'escape' in keys:
            core.quit()
        elif 'space' in keys:
            kb.clearEvents()
            break
    
    # page 3
    displayed_msg.text = ("Every 1300 milliseconds, the dots on each side will "
        "move coherently in either upward or downward direction. For instance, "
        "in the example below, the dots on the left are moving upwards, and "
        "the dots on the right are moving downwards.\n\n\n\n\n\n\n\n\n\n\n"
        "Press 'SPACE' to continue.")
    
    components['stim_left'].dir = 90
    components['stim_right'].dir = 270
    components['stim_left'].coherence = 0.7
    components['stim_right'].coherence = 0.7
    
    while True:
        displayed_msg.draw()
        components['stim_left'].draw()
        components['stim_right'].draw()
        win.flip()
        
        keys = kb.getKeys(keyList=['space', 'escape'])
        if 'escape' in keys:
            core.quit()
        elif 'space' in keys:
            kb.clearEvents()
            break
    
    # page 4
    displayed_msg.text = ("Your objective is to indicate (with the arrow keys "
        "on the keyboard) the side where the dots are moving upwards. For "
        "example, if you see the stimuli below, you should press 'left' arrow "
        "key, because the dots on the left are moving upwards.\n\n\n\n\n\n\n\n\n\n\n"
        "Make the correct choice to continue")
    
    components['stim_left'].dir = 90
    components['stim_right'].dir = 270
    components['stim_left'].coherence = 0.7
    components['stim_right'].coherence = 0.7

    while True:
        displayed_msg.draw()
        components['stim_left'].draw()
        components['stim_right'].draw()
        win.flip()
        
        keys = kb.getKeys(keyList=['left', 'escape'])
        if 'escape' in keys:
            core.quit()
        elif 'left' in keys:
            kb.clearEvents()
            break
            
    # page 5
    displayed_msg.text = ("If you see the stimuli below, you should press "
        "'right' arrow key, because the dots on the right are moving upwards."
        "\n\n\n\n\n\n\n\n\n\nMake the correct choice to continue")
    
    components['stim_left'].dir = 270
    components['stim_right'].dir = 90
    components['stim_left'].coherence = 0.7
    components['stim_right'].coherence = 0.7

    while True:
        displayed_msg.draw()
        components['stim_left'].draw()
        components['stim_right'].draw()
        win.flip()
        
        keys = kb.getKeys(keyList=['right', 'escape'])
        if 'escape' in keys:
            core.quit()
        elif 'right' in keys:
            kb.clearEvents()
            break
            
    # page 5
    displayed_msg.text = ("If you see the stimuli below, you should not press "
        "any keys,because the dots on both sides are moving downwards."
        "\n\n\n\n\n\n\n\n\n\nPress 'SPACE' to continue")
    
    components['stim_left'].dir = 270
    components['stim_right'].dir = 270
    components['stim_left'].coherence = 0.7
    components['stim_right'].coherence = 0.7

    while True:
        displayed_msg.draw()
        components['stim_left'].draw()
        components['stim_right'].draw()
        win.flip()
        
        keys = kb.getKeys(keyList=['space', 'escape'])
        if 'escape' in keys:
            core.quit()
        elif 'space' in keys:
            kb.clearEvents()
            break
    
    # page 6
    displayed_msg.text = ("Remember, the dots are never moving upwards on both "
        "sides at the same time, so you should never press 'left' and 'right' "
        "arrow keys at the same time\n\n\n\n\nPress 'SPACE' to "
        "continue")
    
    components['stim_left'].dir = 270
    components['stim_right'].dir = 90
    components['stim_left'].coherence = 0.7
    components['stim_right'].coherence = 0.7
    
    displayed_msg.draw()
    win.flip()
        
    keys = kb.waitKeys(keyList=['space', 'escape'])
    if 'escape' in keys:
        core.quit()
    kb.clearEvents()

#    # turning pages for instructions
#    i = 0
#    while i < len(params.INS_TEXT):
#        displayed_msg.setText(params.INS_TEXT[i])
#        displayed_msg.draw()
#        win.flip()
#        keys = kb.waitKeys(maxWait=float('inf'), keyList=['space', 'escape'])
#        if 'escape' in keys:
#            core.quit()
#        kb.clearEvents()
#        i += 1

def run_easy_practice(win):
    """
    run an easy practice, used to ensure the participant understood the task,
    it contains 12 trials, 4 left, 4 right and 4 with no target. The cohrence
    is constant, at 0.7; and the stimuli last 750ms with 1850ms of ISI. As the
    task should be very simple, it requires 90% accuracy to continue.
    """
    kb = keyboard.Keyboard()
    components = prepare_stimulus(win)
    
    if params.USE_EYETRACKER:
        io_hub_server = ioHubConnection.ACTIVE_CONNECTION
        eye_tracker = io_hub_server.getDevice('tracker')
    
    displayed_msg = visual.TextStim(win=win, pos=[0,0], height=0.05,
        text="We'll start with an easy practice first, to ensure you understood the task.\n\n\n\nPress 'SPACE' to start")
    displayed_msg.draw()
    win.flip()
    
    keys = kb.waitKeys(maxWait=float('inf'), keyList=['space', 'escape'])
    if 'escape' in keys:
        core.quit()
    kb.clearEvents()
    
    # keep track of accuracy
    accuracy = 0
    n_correct = 0
    n_trials = 0
    
    # start eye tracking
    if params.USE_EYETRACKER:
        io_hub_server.clearEvents()
        eye_tracker.setRecordingState(True)
        
    # do practice until accuracy reaches 100%
    while (accuracy < 0.9):
        correct_answers = ['left'] * 4 + ['right'] * 4 + ['no_target'] * 4
        random.shuffle(correct_answers)
    
        # draw the initial fixation point
        for frameN in range(floor(params.FRAME_RATE * params.FIX_TIME)):
            if ((params.FRAME_RATE*0.5) < frameN < (params.FRAME_RATE*0.5+10)) or (params.FRAME_RATE < frameN < (params.FRAME_RATE+10)):
                win.flip()
            else:
                components['fixation_pt'].draw()
                win.flip()
        
            keys = kb.getKeys()
            if 'escape' in keys:
                core.quit()
            kb.clearEvents()
    
        # start with ISI
        for frameN in range(floor(params.FRAME_RATE * (1850/1000))):
            components['stim_left'].coherence = 0
            components['stim_right'].coherence = 0
                    
            components['fixation_pt'].draw()
            components['stim_left'].draw()
            components['stim_right'].draw()
            win.flip()
                
            keys = kb.getKeys()
            if 'escape' in keys:
                core.quit()
            kb.clearEvents()
    
        # start trial
        for correct_answer in correct_answers:
            n_trials += 1
        
            components['stim_left'].coherence = 0.7
            components['stim_right'].coherence = 0.7
            if correct_answer == 'left':
                components['stim_left'].dir = 90
                components['stim_right'].dir = 270
            elif correct_answer == 'right':
                components['stim_left'].dir = 270
                components['stim_right'].dir = 90
            else:
                components['stim_left'].dir = 270
                components['stim_right'].dir = 270
        
            all_keys = []
            
            # reset keyboard clock for reaction time
            kb.clock.reset()
            first_look = True
            
            # draw stimuli
            for frameN in range(floor(params.FRAME_RATE * (750/1000))):
                components['fixation_pt'].draw()
                components['stim_left'].draw()
                components['stim_right'].draw()
                win.flip()
                keys = kb.getKeys()
                if 'escape' in keys:
                    core.quit()
                else:
                    all_keys.extend(keys)
                    kb.clearEvents()
                
                if params.USE_EYETRACKER:
                    gaze_pos = eye_tracker.getLastGazePosition()
                    valid_gaze_pos = isinstance(gaze_pos, (tuple, list))
                    if valid_gaze_pos and not(components['fixation_region'].contains(gaze_pos)):
                        if first_look: # alert if participant failed to fixate and have not been warned in the current trial
                            components['alert'].play()
                            print('trial ' + str(n_trials) + ' looked away')
                            first_look = False
                
            # ISI
            for frameN in range(floor(params.FRAME_RATE * (1850/1000))):
                components['stim_left'].coherence = 0
                components['stim_right'].coherence = 0
                    
                components['fixation_pt'].draw()
                components['stim_left'].draw()
                components['stim_right'].draw()
                win.flip()
                
                keys = kb.getKeys()
                if 'escape' in keys:
                    core.quit()
                else:
                    all_keys.extend(keys)
                kb.clearEvents()
                
                if params.USE_EYETRACKER:
                    gaze_pos = eye_tracker.getLastGazePosition()
                    valid_gaze_pos = isinstance(gaze_pos, (tuple, list))
                    if valid_gaze_pos and not(components['fixation_region'].contains(gaze_pos)):
                        if first_look: # alert if participant failed to fixate and have not been warned in the current trial
                            components['alert'].play()
                            print('trial ' + str(n_trials) + ' looked away')
                            first_look = False
        
            # calculate accuracy
            if len(all_keys) == 0:
                if correct_answer == 'no_target':
                    n_correct += 1
            else:
                if all_keys[0] == correct_answer:
                    n_correct += 1
                
        accuracy = n_correct / n_trials
        
        # display end of practice messages
        if accuracy >= 0.9:
            print('Accuracy of easy practice block: '+str(round(accuracy, 2))+', continue to hard practice.')
            override = display_end_of_easy_practice(win, redo = False, accuracy = accuracy)
        else:
            print('Accuracy of easy practice block: '+str(round(accuracy, 2))+', re-do the practice.')
            override = display_end_of_easy_practice(win, redo = True, accuracy = accuracy)
        
        if override:
            break
    
    if params.USE_EYETRACKER:
        eye_tracker.setRecordingState(False)
    
    
def run_practice(win, global_clock, trial_clock, output_file):
    """run practice"""
    # run an easy practice first - slow speed, high coherence, to ensure the
    # participant understood the task, requires 100% accuracy to pass
    run_easy_practice(win)
    
    kb = keyboard.Keyboard()
    components = prepare_stimulus(win)
    
    if params.USE_EYETRACKER:
        io_hub_server = ioHubConnection.ACTIVE_CONNECTION
        eye_tracker = io_hub_server.getDevice('tracker')
    
    # display instructions for practice
    displayed_msg = visual.TextStim(win=win, pos=[0,0], height=0.05,
        text="Now we'll do a more challenging practice.\n\nDuring the practice, the difficulty and speed will gradually increase.\n\nYou will need to achieve 50% accuracy during the fastest speed before continuing the experiment.\n\n\n\n\nPress 'SPACE' to start")
    displayed_msg.draw()
    win.flip()

    keys = kb.waitKeys(maxWait=float('inf'), keyList=['space', 'escape'])
    if 'escape' in keys:
        core.quit()
    kb.clearEvents()
    
    # read practice block file
    conditions = read_trial_cond(params.PRACTICE_BLOCK_FILE)
    
    # keep track of accuracy
    accuracy = 0
    n_correct = 0
    n_trials = 0
    
    # if this is a re-do practice
    is_redo = False
    
    # start eye tracking
    if params.USE_EYETRACKER:
        io_hub_server.clearEvents()
        eye_tracker.setRecordingState(True)
        
    # do practice until accuracy reaches 50%
    while (accuracy < 0.5):
        
        # draw the inintal fixation point
        for frameN in range(floor(params.FRAME_RATE * params.FIX_TIME)):
            if ((params.FRAME_RATE*0.5) < frameN < (params.FRAME_RATE*0.5+10)) or (params.FRAME_RATE < frameN < (params.FRAME_RATE+10)):
                win.flip()
            else:
                components['fixation_pt'].draw()
                win.flip()
        
            keys = kb.getKeys()
            if 'escape' in keys:
                core.quit()
            kb.clearEvents()
            
        # start with ISI
        for frameN in range(floor(params.FRAME_RATE * (1850/1000))):
            components['stim_left'].coherence = 0
            components['stim_right'].coherence = 0
                    
            components['fixation_pt'].draw()
            components['stim_left'].draw()
            components['stim_right'].draw()
#           components['fixation_region'].draw()
            win.flip()
                
            keys = kb.getKeys()
            if 'escape' in keys:
                core.quit()
            kb.clearEvents()
        
        # start trials
        for index, row in conditions.iterrows():
            # skip slow trials in redo
            if is_redo and index < params.N_PRACTICE/2:
                continue
                
            update_stims(components, row)
            all_keys = []
            
            # reset keyboard clock for reaction time
            kb.clock.reset()
            first_look = True
            
            # draw stimuli
            for frameN in range(floor(params.FRAME_RATE * (row.stim_duration/1000))):
                components['fixation_pt'].draw()
                components['stim_left'].draw()
                components['stim_right'].draw()
#                components['fixation_region'].draw()
                win.flip()
                keys = kb.getKeys()
                if 'escape' in keys:
                    core.quit()
                else:
                    all_keys.extend(keys)
                kb.clearEvents()
                
                if params.USE_EYETRACKER:
                    gaze_pos = eye_tracker.getLastGazePosition()
                    valid_gaze_pos = isinstance(gaze_pos, (tuple, list))
                    if valid_gaze_pos and not(components['fixation_region'].contains(gaze_pos)):
                        if first_look: # alert if participant failed to fixate and have not been warned in the current trial
                            components['alert'].play()
                            print('trial ' + str(index) + ' looked away')
                            first_look = False
                
            # ISI
            for frameN in range(floor(params.FRAME_RATE * (row.isi/1000))):
                components['stim_left'].coherence = 0
                components['stim_right'].coherence = 0
                    
                components['fixation_pt'].draw()
                components['stim_left'].draw()
                components['stim_right'].draw()
#                components['fixation_region'].draw()
                win.flip()
                
                keys = kb.getKeys()
                if 'escape' in keys:
                    core.quit()
                else:
                    all_keys.extend(keys)
                kb.clearEvents()
                
                if params.USE_EYETRACKER:
                    gaze_pos = eye_tracker.getLastGazePosition()
                    valid_gaze_pos = isinstance(gaze_pos, (tuple, list))
                    if valid_gaze_pos and not(components['fixation_region'].contains(gaze_pos)):
                        if first_look: # alert if participant failed to fixate and have not been warned in the current trial
                            components['alert'].play()
                            print('trial ' + str(index) + ' looked away')
                            first_look = False
            
            # only consider the trials where speed has reached the desired
            if row.stim_duration <= params.STIM_TIME * 1000:
                if len(all_keys) == 0:
                    if row.correct_response == 'no_target':
                        n_correct += 1
                else:
                    if all_keys[0] == row.correct_response:
                        n_correct += 1
        
                n_trials += 1
        
        accuracy = n_correct / n_trials
        
        # display end of practice messages
        if accuracy >= 0.5:
            print('Accuracy of practice block: '+str(round(accuracy, 2))+', continue to experiment.')
            display_end_of_practice(win, redo = False, accuracy = accuracy)
        else:
            is_redo = True
            print('Accuracy of practice block: '+str(round(accuracy, 2))+', re-do the practice.')
            display_end_of_practice(win, redo = True, accuracy = accuracy)
    
    if params.USE_EYETRACKER:
        eye_tracker.setRecordingState(False)
        
        
def run_trials(win, global_clock, trial_clock, output_file, eeg_device):
    """run trials"""
    kb = keyboard.Keyboard()
    components = prepare_stimulus(win)
    block_list = read_block_cond()
    random.shuffle(block_list)
    
    if params.USE_EYETRACKER:
        io_hub_server = ioHubConnection.ACTIVE_CONNECTION
        eye_tracker = io_hub_server.getDevice('tracker')
    
    if len(block_list) != 0:
        cols = read_trial_cond(block_list[0]).columns.values.tolist()
        cols.insert(1, 'block')
        cols.insert(2, 'trial')
        cols.extend(params.OUTPUT_COLS.split(','))
    else:
        print('IMPORTATNT: Empty block list')
        core.quit()
    
    is_first_trial = True
    block_n = 1
    # run each block
    for trial_cond in block_list:
        conditions = read_trial_cond(trial_cond)
        df_block_data = pd.DataFrame(columns=cols)
        
        # keep track of accuracy
        accuracy = 0
        n_correct = 0
        
        # send block start triggers for EEG
        if params.USE_EEG:
            if conditions.condtion.iloc[0] == 0:
                send_triggers(eeg_device, params.TRIG_BLOCK_COND_0_START)
            else:
                send_triggers(eeg_device, params.TRIG_BLOCK_COND_1_START)

        # draw the inintal fixation point
        for frameN in range(floor(params.FRAME_RATE * params.FIX_TIME)):
            if ((params.FRAME_RATE*0.5) < frameN < (params.FRAME_RATE*0.5+10)) or (params.FRAME_RATE < frameN < (params.FRAME_RATE+10)):
                win.flip()
            else:
                components['fixation_pt'].draw()
                win.flip()
            
            keys = kb.getKeys()
            if 'escape' in keys:
                core.quit()
            kb.clearEvents()
            
        # start with ISI
        for frameN in range(floor(params.FRAME_RATE * params.ISI_TIME)):
            components['stim_left'].coherence = 0
            components['stim_right'].coherence = 0
                    
            components['fixation_pt'].draw()
            components['stim_left'].draw()
            components['stim_right'].draw()
            win.flip()
                
            keys = kb.getKeys()
            if 'escape' in keys:
                core.quit()
            kb.clearEvents()
        
        # start trials
        trial_n = 0
        
        # start eye tracking
        if params.USE_EYETRACKER:
            io_hub_server.clearEvents()
            eye_tracker.setRecordingState(True)
       
        for index, row in conditions.iterrows():
            update_stims(components, row)
            all_keys = []
            
            # reset keyboard clock for reaction time
            kb.clock.reset()
            first_look = True
            
            # for EEG triggers
            is_first_frame = True
            
            # draw stimuli
            stimulus_onset_time = global_clock.getTime()
            for frameN in range(floor(params.FRAME_RATE * params.STIM_TIME)):
                components['fixation_pt'].draw()
                components['stim_left'].draw()
                components['stim_right'].draw()
                if params.USE_EEG and is_first_frame:
                    if row.correct_response = 'left':
                        win.callOnFlip(send_triggers, eeg_device, params.TRIG_STIM_ON_LEFT)
                    elif row.correct_response = 'right':
                        win.callOnFlip(send_triggers, eeg_device, params.TRIG_STIM_ON_RIGHT)
                    else:
                        win.callOnFlip(send_triggers, eeg_device, params.TRIG_STIM_ON_NO_TARGET)
                    is_first_frame = False
                else:
                    win.flip()
                    
                keys = kb.getKeys(keyList=['left', 'right'])
                if 'escape' in keys:
                    core.quit()
                else:
                    if params.USE_EEG:
                        for key in keys:
                            if key == 'left':
                                send_triggers(eeg_device, params.TRIG_RESPONSE_LEFT)
                            else:
                                send_triggers(eeg_device, params.TRIG_RESPONSE_RIGHT)
                    all_keys.extend(keys)
                kb.clearEvents()
                
                if params.USE_EYETRACKER:
                    gaze_pos = eye_tracker.getLastGazePosition()
                    valid_gaze_pos = isinstance(gaze_pos, (tuple, list))
                    if valid_gaze_pos and not(components['fixation_region'].contains(gaze_pos)):
                        if first_look: # alert if participant failed to fixate and have not been warned in the current trial
                            components['alert'].play()
                            print('trial ' + str(index) + ' looked away')
                            first_look = False
            
            is_first_frame = True
            stimulus_offset_time = global_clock.getTime()
            # ISI
            for frameN in range(floor(params.FRAME_RATE * params.ISI_TIME)):
                components['stim_left'].coherence = 0
                components['stim_right'].coherence = 0
                    
                components['fixation_pt'].draw()
                components['stim_left'].draw()
                components['stim_right'].draw()
                
                if params.USE_EEG and is_first_frame:
                    if row.correct_response = 'left':
                        win.callOnFlip(send_triggers, eeg_device, params.TRIG_STIM_OFF_LEFT)
                    elif row.correct_response = 'right':
                        win.callOnFlip(send_triggers, eeg_device, params.TRIG_STIM_OFF_RIGHT)
                    else:
                        win.callOnFlip(send_triggers, eeg_device, params.TRIG_STIM_OFF_NO_TARGET)
                    first_frame = False
                else:
                    win.flip()
                
                keys = kb.getKeys()
                if 'escape' in keys:
                    core.quit()
                else:
                    all_keys.extend(keys)
                kb.clearEvents()
                
                if params.USE_EYETRACKER:
                    gaze_pos = eye_tracker.getLastGazePosition()
                    valid_gaze_pos = isinstance(gaze_pos, (tuple, list))
                    if valid_gaze_pos and not(components['fixation_region'].contains(gaze_pos)):
                        if first_look: # alert if participant failed to fixate and have not been warned in the current trial
                            components['alert'].play()
                            print('trial ' + str(index) + ' looked away')
                            first_look = False
            
            # save response data to dataframe
            new_row = row.copy()
            new_row['block'] = block_n - 1
            new_row['trial'] = trial_n
            new_row['key_resp'] = [key.name for key in all_keys]
            new_row['key_resp.rt'] = [key.rt for key in all_keys]
            new_row['stim_onset_time'] = stimulus_onset_time
            new_row['stim_offset_time'] = stimulus_offset_time
            new_row = pd.DataFrame([new_row.to_dict()])
            df_block_data = pd.concat([df_block_data, new_row], ignore_index=True)
            
            
            if len(all_keys) == 0:
                if row.correct_response == 'no_target':
                    n_correct += 1
            else:
                if all_keys[0] == row.correct_response:
                    n_correct += 1
            trial_n += 1
        
        # send block end triggers for EEG
        if params.USE_EEG:
            if conditions.condtion.iloc[0] == 0:
                send_triggers(eeg_device, params.TRIG_BLOCK_COND_0_END)
            else:
                send_triggers(eeg_device, params.TRIG_BLOCK_COND_1_END)
                
        if params.USE_EYETRACKER:
            eye_tracker.setRecordingState(False)
        
        # send data to file
        df_block_data.to_csv(output_file, mode='a', header=is_first_trial, index=False)
        is_first_trial = False
        print('Block '+str(block_n)+' completed. Data saved.')
        print('Accuracy of block '+str(block_n)+': '+str(round(n_correct/trial_n, 2)))
        
        # display end of block info
        if block_n == len(block_list):
            return
        elif block_n % params.BLOCKS_PER_SESSION == 0:
            display_end_of_session(win)
        else:
            display_end_of_block(win, block_n)
        
        block_n += 1


def run_outtro(win):
    """display end of experiment message"""
    kb = keyboard.Keyboard()
    
    displayed_msg = visual.TextStim(win=win, name='welcome_text',
        text="End of experiment!\n\n\nThank you for your participation.\n\nPress 'SPACE' key to close",
        font='Open Sans',
        pos=(0, 0), height=0.05, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);

    displayed_msg.draw()
    win.flip()