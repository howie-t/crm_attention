# import libraries
from psychopy import core, visual, gui, data, event
#from psychopy.hardware import keyboard
#from psychopy.preferences import prefs
from psychopy.tools.filetools import fromFile, toFile
import numpy, random
# import modules
import params
from procedures import setup_window, initialise_exp, calibrate_eyetracker, run_intro, run_practice, run_trials, run_outtro

if __name__ == '__main__':
    output_file = initialise_exp()
    win = setup_window()
    
    # create clocks
    global_clock = core.Clock()
    trial_clock = core.Clock()
    
    if not params.SKIP_INTRO:
        run_intro(win)
    
    if params.USE_EYETRACKER:
        calibrate_eyetracker(win)

    if params.DO_PRACTICE:
        run_practice(win, global_clock, trial_clock, output_file)

    if params.DO_TRIALS:
        run_trials(win, global_clock, trial_clock, output_file)
#    saveData(thisExp=thisExp)

    if not params.SKIP_INTRO:
        run_outtro(win)
        
    event.waitKeys()
    win.close()
    core.quit()