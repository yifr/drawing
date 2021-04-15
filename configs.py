import numpy as np
import json
import os

AVAILABLE_CONFIGS = [
        "TIAN_REPLICATION_0"
        ]

"""
INSTRUCTIONS:

Configs should all share the following format:
     {
      "phases": ['test', 'train', 'generate'],  # Specify what phases the user needs to complete

      "train": # for each phase, specify the ui and data
        {
            "ui_components": [...] # list specifying ui components. Options:
                                    'draw': to collect drawings
                                    'describe': to collect descriptions
                                    'images': to show images
                                    'descriptions': to show existing descriptions

            "images": [...], #list of stimulus images in the order they are to be presented

            (optional) "instructions": [...] # if 'instruct' is in 'ui_components',
                                    this list should have descriptions
                                    for the corresponding images.  
        }
        ... # repeat this for each phase type

        "meta": # General metadata about experiment
            {
                "experiment_id": ...,
                "group_id": ...,
                "prolific_pid": ...,
                etc..., # whatever else needs to be included can go here
            }
        }
"""

def generate_config(experiment_id):
    config = {}

    meta_config = {}
    group_type = 'horizontal' if np.random.random() > 0.5 else 'vertical'
    meta_config['group_type'] = group_type
    meta_config['experiment_id'] = experiment_id
    
    config['meta'] = meta_config

    with open('stims.json', 'r') as f:
        stims = json.load(f)

    if experiment_id == 'TIAN_REPLICATION_0':
        """ 
        Replicating Tian et al. (2020):
            Two groups see an image and draw it.
            For prior elicitation they will only get the test set
            of images
        """
        
        config['phases'] = ['train', 'test']
        train_config = {}
        train_config['ui_components'] = ['images', 'draw']
        train_config['images'] = stims[group_type + '_train']
        config['train'] = train_config

        test_config = {}
        test_config['ui_components'] = ['images', 'draw']
        test_config['images'] = stims['shared_test']
        config['test'] = test_config

    elif experiment_id == 'SOMETHING_ELSE':
        """ 
        Describe experiment
        """
        config['phases'] = ['train', 'test', 'generate']
        phase_config = {}
        phase_config['ui_components'] = []
        phase_config['images'] = []
        phase_config['descriptions'] = [] # if applicable
   
    else:
       return None
    
    return config

if __name__ == '__main__':
    config = generate_config(AVAILABLE_CONFIGS[0])
    print(config)
