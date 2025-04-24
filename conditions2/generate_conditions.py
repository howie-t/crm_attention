# PRACTICE BLOCK: speed from 750 ms -> 250 ms, 60 + 60 trials, contrast pairs
# TRIAL BLOCK 18 * 99 = 1782 trials
# COHRENCE PAIRS: (0.2, 0.9), (0.4, 0.5), (0.4, 0.4), (0.5, 0.4), (0.5, 0.5), (0.9, 0.2)

N_BLOCKS = 18
N_PRACTICE = 140
N_TRIALS = 99 # should be multiples of 3
PERCENT_LEFT = 1/3
PERCENT_RIGHT = 1/3
PERCENT_NO_TARgET = 1 - PERCENT_LEFT - PERCENT_RIGHT
CHOICES = ['left', 'right', 'no_target']
DURATION_MAX = 750
DURATION_MIN = 250
ISI_MAX = 1850
ISI_MIN = 1050
COHERENCES = [0.15, 0.25, 0.4, 0.9]
COHERENCE_SCALING = [2, 1.7, 1.4, 1.2]
CONTRAST_MAX_MULTIPLIER = 10
UP = 90
DOWN = 270

PRACITCE_COHERENCES = [(COHERENCES[0],COHERENCES[3]), (COHERENCES[1],COHERENCES[1]), (COHERENCES[1],COHERENCES[2]), (COHERENCES[2],COHERENCES[1]), (COHERENCES[2],COHERENCES[2]), (COHERENCES[3],COHERENCES[0])]
PRACTICE_N_TRIALS = [24, 24, 24, 24, 24, 24]

CONDITION_1_COHERENCES = [(COHERENCES[0],COHERENCES[3]), (COHERENCES[1],COHERENCES[1]), (COHERENCES[1],COHERENCES[2]), (COHERENCES[2],COHERENCES[1]), (COHERENCES[2],COHERENCES[2])]
CONDITION_1_N_TRIALS = [39, 15, 15, 15, 15]

CONDITION_2_COHERENCES = [(COHERENCES[3],COHERENCES[0]), (COHERENCES[1],COHERENCES[1]), (COHERENCES[1],COHERENCES[2]), (COHERENCES[2],COHERENCES[1]), (COHERENCES[2],COHERENCES[2])]
CONDITION_2_N_TRIALS = [39, 15, 15, 15, 15]

import pandas as pd
import numpy as np
import random
from math import floor

def populate_block(conditions):
    df = pd.DataFrame(columns=['row_id', 'ori_left','ori_right','coherence_left','coherence_right','correct_response'])

    n_trials_total = np.sum(conditions['n_trials'])

    ori_left = []
    ori_right = []
    correct_answers = []

    # iterate through coherence levels and assign answers
    for n_trials in conditions['n_trials']:
        for choice in CHOICES:
            correct_answers_for_coherence = int(n_trials/3) * [choice]
            correct_answers.extend(correct_answers_for_coherence)
            for i in range(len(correct_answers_for_coherence)):
                if correct_answers_for_coherence[i] == 'left':
                    ori_left.append(UP)
                    ori_right.append(DOWN)
                elif correct_answers_for_coherence[i] == 'right':
                    ori_left.append(DOWN)
                    ori_right.append(UP)
                else:
                    ori_left.append(DOWN)
                    ori_right.append(DOWN)
        

    # randomise left & right coherences
    coherence_left = []
    coherence_right = []
    coherence_options = np.array(conditions['coherence_values'])
    coherences = []
    for i, n_trials in enumerate(conditions['n_trials']):
        for j in range(n_trials):
            coherences.append(coherence_options[i])
    coherence_left = [coherence[0] for coherence in coherences]
    coherence_right = [coherence[1] for coherence in coherences]

    # populate values in df
    df.ori_left = ori_left
    df.ori_right = ori_right
    df.coherence_left = coherence_left
    df.coherence_right = coherence_right
    df.correct_response = correct_answers

    df = df.sample(frac=1).reset_index(drop=True)

    df.row_id = list(range(n_trials_total))

    return df

def populate_practice_block(conditions):
    df = populate_block(conditions)
    n_trials_total = np.sum(conditions['n_trials'])
    n_trials_variable = floor(n_trials_total/2)
    n_trials_constant = n_trials_total - n_trials_variable

    # calcualte the stimulus duration for the variable practice trials
    n_trials_before_change = floor(n_trials_variable / (((DURATION_MAX - DURATION_MIN) / 100) + 1))
    durations_variable = []
    trials_until_change = n_trials_before_change
    curr_duration = DURATION_MAX
    for i in range(n_trials_variable):
        if trials_until_change != 0:
            durations_variable.append(curr_duration)
            trials_until_change -= 1
        else:
            if curr_duration > DURATION_MIN:
                curr_duration = curr_duration - 100
            durations_variable.append(curr_duration)
            trials_until_change = n_trials_before_change - 1
    
    # populate the stimulus duration for the fixed-time practice trials
    durations_fixed = np.empty(n_trials_constant, dtype=int)
    durations_fixed.fill(DURATION_MIN)

    df['stim_duration'] = np.concatenate((durations_variable, durations_fixed))

    # calcualte the ISI for the variable practice trials
    n_trials_before_change = floor(n_trials_variable / (((ISI_MAX - ISI_MIN) / 100) + 1))
    isi_variable = []
    trials_until_change = n_trials_before_change
    curr_isi = ISI_MAX
    for i in range(n_trials_variable):
        if trials_until_change != 0:
            isi_variable.append(curr_isi)
            trials_until_change -= 1
        else:
            if curr_isi > ISI_MIN:
                curr_isi = curr_isi - 100
            isi_variable.append(curr_isi)
            trials_until_change = n_trials_before_change - 1

    # populate the ISI for the fixed-time practice trials
    isi_fixed = np.empty(n_trials_constant, dtype=int)
    isi_fixed.fill(ISI_MIN)

    df['isi'] = np.concatenate((isi_variable, isi_fixed))

    # calculate the coherence for the variable practice trials
    n_trials_before_change = floor(n_trials_variable / len(COHERENCE_SCALING))
    trials_until_change = n_trials_before_change
    coherences_left = df.coherence_left.values
    coherences_right = df.coherence_right.values
    new_coherences_left = []
    new_coherences_right = []
    curr_coherence_scale = COHERENCE_SCALING[0]
    idx_scale = 0
    for i in range(n_trials_variable):
        if trials_until_change != 0:
            new_coherence_left = round(coherences_left[i] * curr_coherence_scale, 2)
            if new_coherence_left > 1:
                new_coherence_left = 1
            new_coherence_right = round(coherences_right[i] * curr_coherence_scale, 2)
            if new_coherence_right > 1:
                new_coherence_right = 1

            new_coherences_left.append(new_coherence_left)
            new_coherences_right.append(new_coherence_right)

            trials_until_change -= 1
        else:
            if idx_scale < len(COHERENCE_SCALING) - 1:
                idx_scale += 1
                curr_coherence_scale = COHERENCE_SCALING[idx_scale]

            new_coherence_left = round(coherences_left[i] * curr_coherence_scale, 2)
            if new_coherence_left > 1:
                new_coherence_left = 1
            new_coherence_right = round(coherences_right[i] * curr_coherence_scale, 2)
            if new_coherence_right > 1:
                new_coherence_right = 1
            new_coherences_left.append(new_coherence_left)
            new_coherences_right.append(new_coherence_right)

            trials_until_change = n_trials_before_change - 1

    # concatenate with the original coherences for the fixed-time practice trials
    new_coherences_left = np.concatenate((new_coherences_left, coherences_left[n_trials_variable:]))
    new_coherences_right = np.concatenate((new_coherences_right, coherences_right[n_trials_variable:]))
    df['coherence_left'] = new_coherences_left
    df['coherence_right'] = new_coherences_right

    return df

def populate_conditions():
    # PRACTICE BLOCK: speed from 700 ms -> 250 ms
    practice_conditions = {'coherence_values': PRACITCE_COHERENCES, 'n_trials': PRACTICE_N_TRIALS}
    df = populate_practice_block(practice_conditions)
    df.to_csv('practice_block.csv', mode='w', index = False, header = True)

    for i in range(N_BLOCKS):
        if i%2 == 0:
            conditions = {'coherence_values': CONDITION_1_COHERENCES, 'n_trials': CONDITION_1_N_TRIALS}
            df = populate_block(conditions)
            df['condition'] = 0
        else:
            conditions = {'coherence_values': CONDITION_2_COHERENCES, 'n_trials': CONDITION_2_N_TRIALS}
            df = populate_block(conditions)
            df['condition'] = 1
        df.to_csv('block_'+str(i+1)+'.csv', mode='w', index = False, header = True)
    
def main():
    populate_conditions()

if __name__ == "__main__":
    main()