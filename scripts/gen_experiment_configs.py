"""
gen_experiment_configs.py | Author: Catherine Wong

Generates JSON files containing a complete experimental configuration for human experiments.

Assumes stimuli (images) are in {INPUT_STIMULI_DIR}/S_{N} directories.
Assumes stimuli_set files (containing the full set of stimuli to draw on from the experiment) generated according to: https://github.com/lucast4/drawgood/blob/main_language/language/gen_stimuli_sets.py

Generates JSON files in the following format

Writes out config files to a {CONFIG_DIR}/{EXPERIMENT}_{STIMULI_SET}/{condition}/batch_{N}_shuffle_{N}.json file.

Usage: python gen_experiment_configs.py
        --experiment 0_baselines_priors_a_train-none-draw-describe-sample-interleave
        --output_dir static/configs
        --input_stimuli_set_dir static/stimuli_sets
        --stimuli_set train_images_test_common_s12_s13_neurips_2020  
        --shuffles_per_stimuli_set 1 
        --seed 0
        
"""
import os, json, argparse, random, copy
import pathlib
from datetime import datetime

DEFAULT_OUTPUT_DIR = "static/configs"
INPUT_STIMULI_SET_DIR = 'static/stimuli_sets'
DEFAULT_STIMULI_SET = "train_images_test_common_s12_s13_neurips_2020"


METADATA = "metadata"
CONDITION = "condition"
FULL_CONFIG_PATH = "full_config_path"
EXPERIMENT_ID = "experiment_id"
DESCRIPTION = "description"
TIMESTAMP = "timestamp"
STIMULI_SET = "stimuli_set"
TRAIN = "train"
TEST = "test"
SAMPLING = "sampling"
ALL = "all"

EXPERIMENT_PHASES = "phases"
EXPERIMENT_PHASE = "phase"
UI_COMPONENTS = "ui_components"
IMAGES = "images"

parser = argparse.ArgumentParser()
parser.add_argument("--experiments",
                    nargs="*",
                    required=True,
                    help="Which experiment to generate configurations for. Must be a registered experiment.") 
parser.add_argument('--output_dir', 
                    default=DEFAULT_OUTPUT_DIR,
                    help="Top level directory under which we will write out the experiment configs.")
parser.add_argument("--input_stimuli_set_dir",
                    default=INPUT_STIMULI_SET_DIR,
                    help="Top-level directory where the stimuli sets are stored.")
parser.add_argument("--stimuli_set",
                    default=DEFAULT_STIMULI_SET,
                    help="Stimuli set containing the full dataset of stimuli to generate under.")
parser.add_argument("--train_batch_size_per_phase",
                    default=ALL,
                    help="How many stimuli to show per train phase.")
parser.add_argument("--test_batch_size",
                    default=ALL,
                    help="How many stimuli to show per test phase.")
parser.add_argument("--shuffles_per_stimuli_set",
                    default=1,
                    help="How many complete shuffles to generate for a given stimuli set.")
parser.add_argument("--seed",
                    default=0,
                    help='Random seed.')

EXPERIMENT_CONFIG_GENERATOR_REGISTRY = {}
def register(name):
    def wrapper(f):
        EXPERIMENT_CONFIG_GENERATOR_REGISTRY[name] = f
        return f
    return wrapper

def generate_base_metadata(experiment_id, description, args):
    timestamp = datetime.now().isoformat()
    # Escape the timestamp.
    timestamp = timestamp.replace(":", "-")
    timestamp = timestamp.replace(".", "-")
    return {
        EXPERIMENT_ID: experiment_id,
        DESCRIPTION : description,
        TIMESTAMP : timestamp,
        STIMULI_SET: args.stimuli_set
    }
    
def get_config_dir(experiment_id, args):
    return f"{experiment_id}_{args.stimuli_set}"

def get_config_name(batch, shuffle):
    return f"batch_{batch}_shuffle_{shuffle}.json"

@register("0_baselines_priors__a_train-none__draw-describe-sample-interleave")
def generate_0_baselines_priors_a_train_none_draw_describe_sample_interleave(args, experiment_id, stimuli_set):
    return generate_0_baselines_priors(args, experiment_id, stimuli_set)

def get_test_components_from_experiment_id(experiment_id):
    test_type = experiment_id.split("__")[-1]
    test_1, test_2, sample_type, should_interleave = test_type.split("-")
    if should_interleave == "interleave":
        return [test_1, test_2]
    else:
        print("Not yet implemented")
        assert False
    
def generate_0_baselines_priors(args, experiment_id, stimuli_set):
    all_configs = [] # (config_path, config_data)
    description = "Baseline priors without learning. Uses the draw, describe, and free-generation testing behaviors. Only contains a testing phase for testing tasks."
    metadata = generate_base_metadata(experiment_id, description, args)
    test_tasks = stimuli_set[TEST]
    all_test_stimuli = []
    for condition in test_tasks: 
        all_test_stimuli += test_tasks[condition]
    condition = ALL
    
    config_path = os.path.join(get_config_dir(experiment_id, args), condition)
    for shuffle in range(args.shuffles_per_stimuli_set):
        random.shuffle(all_test_stimuli)
        n_batches = int(all_test_stimuli / args.test_batch_size) + 1 if args.test_batch_size is not ALL else 1
        test_batch_size = args.test_batch_size if args.test_batch_size is not ALL else len(all_test_stimuli)
        for batch in range(n_batches):
            config_name = get_config_name(batch, shuffle)
            full_config_path = os.path.join(config_path, config_name)
            
            start = batch * test_batch_size
            image_batch = all_test_stimuli[start:start+test_batch_size]
            
            config_data = dict()
            config_data[METADATA] = copy.copy(metadata)
            config_data[METADATA][CONDITION] = condition
            config_data[METADATA][FULL_CONFIG_PATH] = full_config_path
            config_data[EXPERIMENT_PHASES] = []
            # Draw and describe
            phase = f"{EXPERIMENT_PHASE}_1"
            config_data[EXPERIMENT_PHASES].append(phase)
            phase_config = dict()
            phase_config[IMAGES] = image_batch
            phase_config[UI_COMPONENTS] = [IMAGES] + get_test_components_from_experiment_id(experiment_id)
            config_data[phase] = phase_config
            # Sample
            phase = f"{EXPERIMENT_PHASE}_2"
            config_data[EXPERIMENT_PHASES].append(phase)
            phase_config = dict()
            phase_config[IMAGES] = []
            phase_config[SAMPLING] = True
            phase_config[UI_COMPONENTS] =  get_test_components_from_experiment_id(experiment_id)
            config_data[phase] = phase_config
            
            all_configs.append((full_config_path, config_data))
    return all_configs

def set_random_seed(args):
    random.seed(args.seed)
    
def load_stimuli_set(args):
    stimuli_path = os.path.join(args.input_stimuli_set_dir, args.stimuli_set + ".json")
    with open(stimuli_path, 'r') as f:
        return json.load(f)
    
def iteratively_generate_experiment_configs(args, stimuli_set):
    for experiment in args.experiments:
        if experiment not in EXPERIMENT_CONFIG_GENERATOR_REGISTRY:
            print(f"Experiment config not found: {experiment}")
            assert False
        experiment_config_generator_fn = EXPERIMENT_CONFIG_GENERATOR_REGISTRY[experiment]
        config_data = experiment_config_generator_fn(args, experiment, stimuli_set)
        
        for config_path, config in config_data:
            output_dir = os.path.join(args.output_dir, os.path.dirname(config_path))
            pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)
            full_config_path = os.path.join(args.output_dir, config_path)
            print(f"Writing out config to: {full_config_path}")
            with open(full_config_path, 'w') as f:
                json.dump(config, f) 
                
def main(args):
    set_random_seed(args)
    stimuli_set = load_stimuli_set(args)
    iteratively_generate_experiment_configs(args, stimuli_set)

if __name__ == '__main__':
  args = parser.parse_args()
  main(args)