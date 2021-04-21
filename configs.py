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
        
        config['phases'] = ['phase_1', 'phase_2']
        phase_1_config = {}
        phase_1_config['ui_components'] = ['images', 'draw', 'describe']
        phase_1_config['images'] = stims[group_type + '_train']
        config['phase_1'] = phase_1_config

        phase_2_config = {}
        phase_2_config['ui_components'] = ['images', 'draw', 'describe']
        phase_2_config['images'] = stims['shared_test']
        config['phase_2'] = phase_2_config
        
        return config

    elif experiment_id == 'sampleImg':
        config['phases'] = ['phase_1']
        phase_1_config = {}
        phase_1_config['ui_components'] = ['draw']
        phase_1_config['images'] = [None for i in range(10)]
        phase_1_config['sampling'] = True
        config['phase_1'] = phase_1_config
        
        return config

    elif experiment_id == 'sampleText':
        config['phases'] = ['phase_1']
        phase_1_config = {}
        phase_1_config['ui_components'] = ['describe']
        phase_1_config['images'] = [None for i in range(10)]
        phase_1_config['sampling'] = True
        config['phase_1'] = phase_1_config
        
        return config
    
    elif experiment_id == 'sampleAll':
        config['phases'] = ['phase_1']
        phase_1_config = {}
        phase_1_config['ui_components'] = ['draw', 'describe']
        phase_1_config['images'] = [None for i in range(10)]
        phase_1_config['sampling'] = True
        config['phase_1'] = phase_1_config
        
        return config
    
    elif experiment_id == 'drawOnly':
        config['phases'] = ['phase_1', 'phase_2']
        phase_1_config = {}
        phase_1_config['ui_components'] = ['images', 'draw']
        phase_1_config['images'] = stims[group_type + '_train']
        config['phase_1'] = phase_1_config

        phase_2_config = {}
        phase_2_config['ui_components'] = ['images', 'draw', 'describe']
        phase_2_config['images'] = stims['shared_test']
        config['phase_2'] = phase_2_config
        
        return config
    
    elif experiment_id == 'describeOnly':
        config['phases'] = ['phase_1', 'phase_2']
        phase_1_config = {}
        phase_1_config['ui_components'] = ['images', 'describe']
        phase_1_config['images'] = stims[group_type + '_train']
        config['phase_1'] = phase_1_config

        phase_2_config = {}
        phase_2_config['ui_components'] = ['images', 'draw', 'describe']
        phase_2_config['images'] = stims['shared_test']
        config['phase_2'] = phase_2_config
        
        return config

    elif experiment_id  == 'readDescriptions':
        word_file = "/usr/share/dict/words"
        WORDS = open(word_file).read().splitlines()

        config['phases'] = ['phase_1', 'phase_2']
        phase_1_config = {}
        phase_1_config['ui_components'] = ['descriptions', 'draw', 'describe']
        phase_1_config['images'] = stims[group_type + '_train']
        n_images = len(phase_1_config['images'])
        phase_1_config['descriptions'] = [' '.join(np.random.choice(WORDS, np.random.randint(5, 10))) for i in range(n_images)]
        config['phase_1'] = phase_1_config

        phase_2_config = {}
        phase_2_config['ui_components'] = ['descriptions', 'draw', 'describe']
        phase_2_config['images'] = stims['shared_test']
        n_images = len(phase_2_config['images'])
        phase_2_config['descriptions'] = [' '.join(np.random.choice(WORDS, np.random.randint(4,8))) for i in range(n_images)]
        config['phase_2'] = phase_2_config
        
        return config

    elif experiment_id == 'bothStims':
        word_file = "/usr/share/dict/words"
        WORDS = open(word_file).read().splitlines()

        config['phases'] = ['phase_1', 'phase_2']
        phase_1_config = {}
        phase_1_config['ui_components'] = ['descriptions', 'images', 'draw', 'describe']
        phase_1_config['images'] = stims[group_type + '_train']
        n_images = len(phase_1_config['images'])
        phase_1_config['descriptions'] = [' '.join(np.random.choice(WORDS, np.random.randint(5, 10))) for i in range(n_images)]
        config['phase_1'] = phase_1_config

        phase_2_config = {}
        phase_2_config['ui_components'] = ['descriptions', 'images', 'draw', 'describe']
        phase_2_config['images'] = stims['shared_test']
        n_images = len(phase_2_config['images'])
        phase_2_config['descriptions'] = [' '.join(np.random.choice(WORDS, np.random.randint(4,8))) for i in range(n_images)]
        config['phase_2'] = phase_2_config
        
        return config

    
    return config

    

if __name__ == '__main__':
    config = generate_config(AVAILABLE_CONFIGS[0])
    print(config)
