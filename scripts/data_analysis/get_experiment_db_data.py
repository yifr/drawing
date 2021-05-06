"""
get_experiment_db_data.py | Author : Catherine Wong.
Utility functions to download data from the MongoDB experiment server for various experiment groups.
This file is oriented towards experiment replication: it contains fine-grained rules for determining what to download from the server for each experiment group (eg. drawlang_X.X), and creates metadata files about each experiment group.

This writes out data to:
    data_experiment/drawlang_X.X/raw/raw_experiment_data.json
We currently group all of the experiments (and their conditions) into one file.
        metadata: metadata about the experiment group
        experiment_ids: dict from experiment_id to data for that experiment.
            <experiment_id> : 
                summary: summary statistics on the experiment
                conditions : {condition : [list of users in that condition]}
                images: {user : [ordered list of image paths seen by a user, or SAMPLE_X for samples]}
                metadata : {user: experiment metadata}
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
    description = "0.0 - internal pilot. Compares 0_baseline, 1_provided_language with drawing, 3_producing_language with/without drawing. Only keeps admin user data."
    experiment_ids = [
        "0_baselines_priors__train-none__test-default__neurips_2020",
        "1_no_provided_language__train-im-dr__test-default__neurips_2020",
        "3_producing_language__train-im-de__test-default__neurips_2020",
        "3_producing_language__train-im-dr-de__test-default__neurips_2020"
    ]
    def exclusion_users(user_id):
        for admin_id in ['hope', 'cathy', 'yoni', 'admin']:
            if admin_id in user_id: return False
        return True
        
    filters = {EXCLUSION_USERS : exclusion_users}
    return get_experiment_group_data(args, experiment_group, description, experiment_ids, filters)

@register_group("0.1")
def download_data_0_0(args, experiment_group):
    description = "0.0 - external pilot. Compares 0_baseline, 1_provided_language with drawing, 3_producing_language with/without drawing."
    experiment_ids = [
        "0_baselines_priors__train-none__test-default__neurips_2020",
        "1_no_provided_language__train-im-dr__test-default__neurips_2020",
        "3_producing_language__train-im-de__test-default__neurips_2020",
        "3_producing_language__train-im-dr-de__test-default__neurips_2020"
    ]
    def exclusion_users(user_id):
        for admin_id in ['hope', 'cathy', 'yoni', 'admin']:
            if admin_id in user_id: return True
        return False
        
    filters = {EXCLUSION_USERS : exclusion_users}
    return get_experiment_group_data(args, experiment_group, description, experiment_ids, filters)

### Utility functions for getting data.``
def get_experiment_group_data(args, experiment_group, description, experiment_ids, filters):
    experiment_data = {}
    # Generate base metadata.
    metadata = generate_base_metadata(args, experiment_group, description, experiment_ids)
    experiment_data[METADATA] = metadata
    
    # Download data for each experiment.
    experiment_data[EXPERIMENT_IDS] = {
        experiment_id : get_all_experiment_data(experiment_id, filters) for experiment_id in experiment_ids 
    }
    return experiment_data

def get_all_experiment_data(experiment_id, filters):
    # Update the experiment metadata
    experiment_dict = {
        SUMMARY : None,
        METADATA : defaultdict(list),
        CONDITIONS : defaultdict(list),
        IMAGES : defaultdict(list),
        STROKES : defaultdict(list),
        DESCRIPTIONS : defaultdict(list)
    }
    for record in db_utils.all_experiment_records(experiment_id):
        user_id = record[METADATA][USER_ID]
        
        if EXCLUSION_USERS in filters:
            exclusion_user_fn = filters[EXCLUSION_USERS]
            if exclusion_user_fn(user_id): continue
        
        experiment_dict[METADATA][user_id].append(record[METADATA])
        
        condition = record[METADATA][CONDITION]
        experiment_dict[CONDITIONS][condition].append(user_id)
        
        all_user_images, all_user_strokes, all_user_descriptions = [], [], []
        for phase in record[EXPERIMENT_PHASES]:
            if IMAGES in record[phase]:
                all_user_images += record[phase][IMAGES]
            if STROKES in record[phase]:
                all_user_strokes += record[phase][STROKES]
            if USER_DESCRIPTIONS in record[phase]:
                all_user_descriptions += record[phase][USER_DESCRIPTIONS]
        experiment_dict[IMAGES][user_id], experiment_dict[STROKES][user_id], experiment_dict[DESCRIPTIONS][user_id] = all_user_images, all_user_strokes, all_user_descriptions
    experiment_dict[SUMMARY] = {
        TOTAL_USERS : sum(len(users) for users in experiment_dict[CONDITIONS].values())
    }
    return experiment_dict

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