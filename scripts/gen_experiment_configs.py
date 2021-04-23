"""
gen_experiment_configs.py | Author: Catherine Wong

Generates JSON files containing a complete experimental configuration for human experiments.

Assumes stimuli (images) are in {INPUT_STIMULI_DIR}/S_{N} directories.
Assumes stimuli_set files (containing the full set of stimuli to draw on from the experiment) generated according to: https://github.com/lucast4/drawgood/blob/main_language/language/gen_stimuli_sets.py

Generates JSON files in the following format: (see configs.py)

Writes out config files to a {CONFIG_DIR}/{EXPERIMENT}_{STIMULI_SET}/{condition}/batch_{N}_shuffle_{N}.json file.

Usage: python gen_experiment_configs.py
        --experiment 0_baselines_priors_a_train-none-draw-describe-sample-interleave
        --output_dir static/configs
        --input_stimuli_set_dir static/stimuli_sets
        --language_set train_images_test_common_s12_s13_neurips_2020 
        --stimuli_set train_images_test_common_s12_s13_neurips_2020  
        --shuffles_per_stimuli_set 1 
        --seed 0
        
"""
import os, json, argparse, random, copy
import pathlib
from datetime import datetime
from collections import defaultdict

DEFAULT_OUTPUT_DIR = "static/configs"
INPUT_STIMULI_SET_DIR = 'static/stimuli_sets'
DEFAULT_STIMULI_SET = "train_images_test_common_s12_s13_neurips_2020"
INPUT_LANGUAGE_SET_DIR = "static/language_sets"
DEFAULT_LANGUAGE_SET = "toy_train_common_test_common_s12_s13_neurips_2020"

METADATA = "metadata"
CONDITIONS = "conditions"
CONDITION = "condition"
FULL_CONFIG_PATH = "full_config_path"
EXPERIMENT_ID = "experiment_id"
DESCRIPTION = "description"
DESCRIPTIONS = "descriptions"
LANGUAGE = "language"
TIMESTAMP = "timestamp"
LANGUAGE_SET = "language_set"
STIMULI_SET = "stimuli_set"
TRAIN = "train"
TEST = "test"
SAMPLE = 'sample'
SAMPLING = "sampling"
ALL = "all"

EXPERIMENT_PHASES = "phases"
EXPERIMENT_PHASE = "phase"
UI_COMPONENTS = "ui_components"
IMAGES = "images"

SAMPLING_DEFAULT_BATCH_SIZE = 10

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
parser.add_argument("--input_language_set_dir",
                    default=INPUT_LANGUAGE_SET_DIR,
                    help="Top-level directory where the langauge for stimuli sets are stored.")
parser.add_argument("--language_set",
                    default=None,
                    help="Language set containing accompanying language.")
parser.add_argument("--train_batch_size_per_phase",
                    default=ALL,
                    help="How many stimuli to show per train phase.")
parser.add_argument("--test_batch_size",
                    default=ALL,
                    help="How many stimuli to show per test phase.")
parser.add_argument("--sampling_batch_size",
                    default=SAMPLING_DEFAULT_BATCH_SIZE,
                    help="How many samples to select during sampling phases.")
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
        STIMULI_SET: args.stimuli_set,
        LANGUAGE_SET: args.language_set
    }
    
def get_config_dir(experiment_id, args):
    return f"{experiment_id}_{args.stimuli_set}"

def get_config_name(batch, shuffle):
    return f"batch_{batch}_shuffle_{shuffle}.json"

def get_phase_name(phase_num):
    return f"{EXPERIMENT_PHASE}_{phase_num}"

@register("0_baselines_priors__a_train-none__draw-describe-sample-interleave")
def generate_0_baselines_priors_a_train_none_draw_describe_sample_interleave(args, experiment_id, stimuli_set):
    return generate_0_baselines_priors(args, experiment_id, stimuli_set)

@register("0_baselines_priors__a_train-none__describe-draw-sample-interleave")
def generate_0_baselines_priors_a_train_none_describe_draw_sample_interleave(args, experiment_id, stimuli_set):
    return generate_0_baselines_priors(args, experiment_id, stimuli_set)
    
def generate_0_baselines_priors(args, experiment_id, stimuli_set):
    all_configs = [] # (config_path, config_data)
    description = "Baseline priors without learning. Uses the draw, describe, and free-generation testing behaviors. Only contains a testing phase for testing tasks."
    metadata = generate_base_metadata(experiment_id, description, args)
    test_tasks = stimuli_set[TEST]
    all_test_stimuli = []
    for condition in test_tasks: 
        for stimuli_sub_group in test_tasks[condition]:
            all_test_stimuli += stimuli_sub_group
    condition = ALL
    conditions = [ALL]
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
            config_data[METADATA][CONDITIONS] = conditions
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
            phase_config[IMAGES] = [None] * args.sampling_batch_size
            phase_config[SAMPLING] = True
            phase_config[UI_COMPONENTS] =  get_test_components_from_experiment_id(experiment_id)
            config_data[phase] = phase_config
            
            all_configs.append((full_config_path, config_data))
    return all_configs

@register("1_no_provided_language__a_train-images__draw-describe-sample-interleave")
def generate_1_no_provided_language_a_train_images__draw_describe_sample_interleave(args, experiment_id, stimuli_set):
    return generate_1_no_provided_language(args, experiment_id, stimuli_set)

@register("1_no_provided_language__b_train-images-draw__draw-describe-sample-interleave")
def generate_1_no_provided_language_a_train_images_draw__draw_describe_sample_interleave(args, experiment_id, stimuli_set):
    return generate_1_no_provided_language(args, experiment_id, stimuli_set)
    
def generate_1_no_provided_language(args, experiment_id, stimuli_set):
    description = "No provided language during training. Conditions on different image stimuli during training. Uses the draw, describe, and free-generation testing behaviors."
    return generate_batched_train_test_configs(args, description, experiment_id, stimuli_set)

@register("2_provided_language__a_train-images-descriptions__draw-describe-sample-interleave")
def generate_2_provided_language__a_train_images_descriptions__draw_describe_sample_interleave(args, experiment_id, stimuli_set):
    return generate_2_provided_language(args, experiment_id, stimuli_set)

@register("2_provided_language__b_train-images-descriptions-draw__draw-describe-sample-interleave")
def generate_2_provided_language__b_train_images_draw_descriptions__draw_describe_sample_interleave(args, experiment_id, stimuli_set):
    return generate_2_provided_language(args, experiment_id, stimuli_set)
    
def generate_2_provided_language(args, experiment_id, stimuli_set):
    description = "Provided language during training. Conditions on different language stimuli during training; images are the same. Uses the draw, describe, and free-generation testing behaviors."
    return generate_batched_train_test_configs(args, description, experiment_id, stimuli_set)

@register("3_producing_language__a_train-images-describe__draw-describe-sample-interleave")
def generate_3_producing_language_a_train_images_describe__draw_describe_sample_interleave(args, experiment_id, stimuli_set):
    return generate_3_producing_language(args, experiment_id, stimuli_set)

@register("3_producing_language__b_train-images-draw-describe__draw-describe-sample-interleave")
def generate_3_producing_language_a_train_images_draw_describe__draw_describe_sample_interleave(args, experiment_id, stimuli_set):
    return generate_3_producing_language(args, experiment_id, stimuli_set)
    
def generate_3_producing_language(args, experiment_id, stimuli_set):
    description = "Language production during training. Conditions on different image stimuli during training. Uses the draw, describe, and free-generation testing behaviors."
    return generate_batched_train_test_configs(args, description, experiment_id, stimuli_set)

def get_n_batches_for_condition(args, condition, stimuli_set):
    """Gets the maximum number of batches given the specified train and test batch sizes"""
    n_stimuli_per_train_phase = [len(phase) for phase in stimuli_set[TRAIN][condition]] 
    n_stimuli_per_test_phase = len(stimuli_set[TEST].get(condition, [])) + len(stimuli_set[TEST].get(ALL, []))
    
    max_stimuli_per_train_phase = max(n_stimuli_per_train_phase)
    n_train_batches = int(max_stimuli_per_train_phase / args.train_batch_size_per_phase) + 1 if args.train_batch_size_per_phase is not ALL else 1
    
    n_test_batches = int(n_stimuli_per_test_phase / args.test_batch_size) + 1 if args.test_batch_size is not ALL else 1
    return max(n_train_batches, n_test_batches)

def generate_batched_train_test_configs(args, description, experiment_id, stimuli_set):
    all_configs = defaultdict(lambda: defaultdict()) # (config_path, config_data)
    
    metadata = generate_base_metadata(experiment_id, description, args)
    n_sample_phases = 1 if SAMPLE in experiment_id else 0 
    conditions = list(stimuli_set[TRAIN].keys())
    total_n_train_phases = len(stimuli_set[TRAIN][conditions[0]])
    total_n_test_phases = len(stimuli_set[TEST].get(conditions[0], [])) + len(stimuli_set[TEST].get(ALL, [])) + n_sample_phases        
            
    for shuffle in range(args.shuffles_per_stimuli_set):
        for condition in conditions:
            config_path = os.path.join(get_config_dir(experiment_id, args), condition)
            # Calculate the number of 'batches' in advance based on the length of the phases.
            total_n_batches = get_n_batches_for_condition(args, condition, stimuli_set)
            
            # Initialize all of the batches and their metadata.
            for batch in range(total_n_batches):
                config_name = get_config_name(batch, shuffle)
                full_config_path = os.path.join(config_path, config_name)
                config_data = dict()
                config_data[METADATA] = copy.copy(metadata)
                config_data[METADATA][CONDITION] = condition
                config_data[METADATA][FULL_CONFIG_PATH] = full_config_path
                config_data[EXPERIMENT_PHASES] = [get_phase_name(phase_num) for phase_num in range(1, total_n_train_phases + total_n_test_phases + 1 )]
                all_configs[full_config_path] = config_data
            
            # Build train phases
            for train_phase_idx, train_phase_stimuli in enumerate(stimuli_set[TRAIN][condition]):
                phase_name = get_phase_name(train_phase_idx + 1)
                random.shuffle(train_phase_stimuli)
                batch_size = args.train_batch_size_per_phase if args.train_batch_size_per_phase is not ALL else len(train_phase_stimuli)
                for batch in range(total_n_batches):
                    config_name = get_config_name(batch, shuffle)
                    full_config_path = os.path.join(config_path, config_name)
                    config_data = all_configs[full_config_path]
                    
                    batch_start = batch * batch_size
                    batch_end = batch_start + batch_size
                    if batch_start > len(train_phase_stimuli):
                        # TODO (cathywong): this won't actually wrap around.
                        assert False
                    config_data[phase_name] = get_train_phase_config(args, experiment_id, condition, train_phase_stimuli, batch_start, batch_end)
            # Build test phases that aren't sampling based
            test_stimuli_phases = stimuli_set[TEST].get(conditions[0], []) + stimuli_set[TEST].get(ALL, [])
            for test_phase_idx, test_phase_stimuli in enumerate(test_stimuli_phases):
                phase_name = get_phase_name(test_phase_idx + total_n_train_phases + 1)
                random.shuffle(test_phase_stimuli)
                batch_size = args.test_batch_size if args.test_batch_size is not ALL else len(test_phase_stimuli)
                for batch in range(total_n_batches):
                    config_name = get_config_name(batch, shuffle)
                    full_config_path = os.path.join(config_path, config_name)
                    config_data = all_configs[full_config_path]
                    
                    batch_start = batch * batch_size
                    batch_end = batch_start + batch_size
                    if batch_start > len(test_phase_stimuli):
                        # TODO (cathywong): this won't actually wrap around.
                        assert False
                    config_data[phase_name] = get_test_phase_config(experiment_id, test_phase_stimuli, batch_start, batch_end, sampling=False)
            # Finally, the test phase
            for sample_phase_idx in range(n_sample_phases):
                for batch in range(total_n_batches):
                    config_name = get_config_name(batch, shuffle)
                    full_config_path = os.path.join(config_path, config_name)
                    config_data = all_configs[full_config_path]
                    phase_name = get_phase_name(total_n_train_phases + total_n_test_phases)
                    config_data[phase_name] = get_test_phase_config(experiment_id, None, None, None, sampling=True)
    return all_configs.items()

def get_description_for_images(args, condition, image_batch):
    full_language_set = os.path.join(args.input_language_set_dir, args.language_set + ".json")
    with open(full_language_set, 'r') as f:
        language_data = json.load(f)
    return [language_data[LANGUAGE][condition][image][0] for image in image_batch]

def get_train_phase_config(args, experiment_id, condition, train_phase_stimuli, batch_start, batch_end):
    phase_config = dict()
    image_batch = train_phase_stimuli[batch_start:batch_end]
    phase_config[IMAGES] = image_batch
    phase_config[SAMPLING] = False
    phase_config[UI_COMPONENTS] =  get_train_components_from_experiment_id(experiment_id)
    if DESCRIPTIONS in phase_config[UI_COMPONENTS]:
        phase_config[DESCRIPTIONS] = get_description_for_images(args, condition, image_batch)
    return phase_config


def get_train_components_from_experiment_id(experiment_id):
    train_type = experiment_id.split("__")[1]
    train_components = train_type.split(TRAIN)[-1]
    ui_components = [comp for comp in train_components.split("-") if len(comp) > 0]
    return ui_components
    
def get_test_phase_config(experiment_id, test_phase_stimuli, batch_start, batch_end, sampling=False):
    phase_config = dict()
    image_batch = test_phase_stimuli[batch_start:batch_end] if not sampling else [None] * args.sampling_batch_size    
    phase_config[SAMPLING] = sampling
    phase_config[IMAGES] = image_batch
    phase_config[UI_COMPONENTS] = [IMAGES] if not sampling else []
    phase_config[UI_COMPONENTS] += get_test_components_from_experiment_id(experiment_id)
    return phase_config
                
def get_test_components_from_experiment_id(experiment_id):
    test_type = experiment_id.split("__")[-1]
    test_1, test_2, sample_type, should_interleave = test_type.split("-")
    if should_interleave == "interleave":
        return [test_1, test_2]
    else:
        print("Not yet implemented")
        assert False
        
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