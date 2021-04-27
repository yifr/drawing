import os
import json
import numpy as np

condition = 'all'
exp_path = os.path.join('static/configs')
experiment_configs = []
for root, dirs, files in os.walk(exp_path, topdown=False):
        dirs = [d for d in dirs if d == condition]
        for name in files:
            print(name)
            fname = os.path.join(root, name)
            experiment_configs.append(fname)

print(len(experiment_configs))
config_path = np.random.choice(experiment_configs)
config = json.load(open(config_path, 'r'))
print(config, experiment_configs)
