"""
get_experiment_db_data.py | Author : Catherine Wong.
Utility functions to download data from the MongoDB experiment server for various experiment groups.
This file is oriented towards experiment replication: it contains fine-grained rules for determining what to download from the server for each experiment group (eg. drawlang_X.X), and creates metadata files about each experiment group.

This writes out data to:
    data_experiment/drawlang_X.X/raw/raw_experiment_data.json
We currently group all of the experiments (and their conditions) into one file.
        metadata: metadata about the experiment group, including summary statistics on the experiment.
        experiment_ids: dict from experiment_id to data for that experiment.
            <experiment_id> : 
                conditions : {condition : [list of users in that condition]}
                images: {user : [ordered list of image paths seen by a user, or SAMPLE_X for samples]}
                strokes: {user : [ordered list of [stroke arrays] corresponding to images]}
                descriptions : {user : [ordered list of descriptions corresponding to images]}

Usage:
    get_experiment_db_data.py --experiment_group 0.0
"""
DEFAULT_TOP_LEVEL_OUTPUT_DIR = "data_experiment"
DEFAULT_EXPERIMENT_DIR = "laps_{}/raw"
DEFAULT_OUTPUT_DATA_FILE = "raw_experiment_data.json"

import os, json, argparse, random, copy
import pathlib
from datetime import datetime
from collections import defaultdict

import db_utils
from experiment_constants import *

parser = argparse.ArgumentParser()
parser.add_argument("--experiment_group",
                    required=True,
                    help="Which experiment group to download data for.") 
parser.add_argument('--output_dir', 
                    default=DEFAULT_TOP_LEVEL_OUTPUT_DIR,
                    help="Top level directory under which we will write out the experiment data.")

# Registered experiments groups. Each one of these determines which experiment_ids we cluster together, exclusions on the user_ids, etc.
EXPERIMENT_GROUP_REGISTRY = {}
def register_group(name):
    def wrapper(f):
        EXPERIMENT_GROUP_REGISTRY[name] = f
        return f
    return wrapper
    
@register_group("0.0")
def download_data_0_0(args, experiment_group):
    description = "0.0 - internal pilot. Compares 0_baseline, 1_provided_language with drawing, 3_producing_language with/without drawing."
    experiment_ids = [
        "0_baselines_priors__train-none__test-default__neurips_2020",
        "1_no_provided_language__train-im-dr__test-default__neurips_2020",
        "3_producing_language__train-im-de__test-default__neurips_2020",
        "3_producing_language__train-im-dr-de__test-default__neurips_2020"
    ]
    return get_experiment_group_data(args, experiment_group, description, experiment_ids)

### Utility functions for getting data.``
def get_experiment_group_data(args, experiment_group, description, experiment_ids):
    experiment_data = {}
    # Generate base metadata.
    metadata = generate_base_metadata(args, experiment_group, description, experiment_ids)
    experiment_data[METADATA] = metadata
    
    # Download data for each experiment.
    experiment_data[EXPERIMENT_IDS] = {
        experiment_id : get_all_experiment_data(experiment_id) for experiment_id in experiment_ids
    }
    return experiment_data

def get_all_experiment_data(experiment_id):
    for record in db_utils.all_experiment_records(experiment_id):
        import pdb; pdb.set_trace()

def generate_base_metadata(args, experiment_group, description, experiment_ids):
    timestamp = datetime.now().isoformat()
    # Escape the timestamp.
    timestamp = timestamp.replace(":", "-")
    timestamp = timestamp.replace(".", "-")
    return {
        EXPERIMENT_GROUP: experiment_group,
        EXPERIMENT_IDS : experiment_ids,
        DESCRIPTION : description,
        TIMESTAMP : timestamp,
    }

    
def download_data_for_experiments(args):
    """Downloads and writes out data for the experiment indicated in experiment_group."""
    experiment_group = args.experiment_group
    if experiment_group not in EXPERIMENT_GROUP_REGISTRY:
        print(f"Experiment group not found: {experiment_group}")
        assert False
    
    experiment_group_download_fn = EXPERIMENT_GROUP_REGISTRY[experiment_group]
    experiment_data = experiment_group_download_fn(args, experiment_group)
    
    output_dir = os.path.join(args.output_dir, DEFAULT_EXPERIMENT_DIR.format(experiment_group))
    pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_path = os.path.join(output_dir, DEFAULT_OUTPUT_DATA_FILE)
    print(f"Writing out experiment group data to: {output_path}")
    with open(output_path, 'w') as f:
        json.dump(experiment_data, f) 

def main(args):
    download_data_for_experiments(args)

if __name__ == '__main__':
  args = parser.parse_args()
  main(args)