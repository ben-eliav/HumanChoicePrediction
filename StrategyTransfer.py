import utils
import environments
from consts import *
from utils.functions import *
import wandb
from utils import personas
import argparse
from utils.datasets import OfflineDataSet

parser = argparse.ArgumentParser(description='Hyperparameter tuning with wandb.')
def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

# General Features
parser.add_argument('--ENV_HPT_mode', type=str2bool, default=False, help='Enable/disable HPT mode')
parser.add_argument('--seed', type=int, default=1, help='Random seed')
parser.add_argument('--task', choices=["off_policy", "on_policy"], default="off_policy", help='Task')
parser.add_argument('--ENV_LEARNING_RATE', type=float, default=1e-3, help='Learning rate')
parser.add_argument('--loss_weight_type', type=str, default="None", help='Loss weight type')
parser.add_argument('--save_artifacts', type=str2bool, default=True, help='Save artifacts flag')
parser.add_argument('--strategies', default=None, help='Which strategies are include the training data')
parser.add_argument('--total_epochs', type=int, default=25, help='Number of epochs during training')

# Input Features
parser.add_argument('--features', type=str, default="EFs", help='Input features')

# Architecture Features
parser.add_argument('--architecture', type=str, default="LSTM", help='Model architecture')
parser.add_argument('--hidden_dim', type=int, default=32, help='Hidden dimensions')
parser.add_argument('--layers', type=int, default=2, help='Number of layers')
parser.add_argument('--transformer_nheads', type=int, default=4, help='Transformer heads')
parser.add_argument('--dropout', type=float, default=0, help='Dropout rate')

# Human data
parser.add_argument('--human_train_size', type=int, default=210, help='Training set size (in No. of users)')

# Online Simulation
parser.add_argument('--online_sim_type', type=str, default="before_epoch", help='Online simulation type')
parser.add_argument('--basic_nature', type=int, default=12, help='Basic nature of simulation')
parser.add_argument('--online_simulation_factor', type=float, default=4, help='Online simulation factor')
parser.add_argument('--simulation_bot_per_user', type=int, default=6, help='Simulation bot per user')
parser.add_argument('--simulation_signal_error', type=float, default=0.3, help='Simulation signal error')
parser.add_argument('--simulation_user_improve', type=float, default=0.01,
                    help='Simulation user improvement rate - (eta from Shapira et al. 2023)')
parser.add_argument('--max_games', type=int, default=4, help='Maximum games between sim. user and bot where eta==0')
parser.add_argument('--zero_knowledge', type=str2bool, default=True, help='Zero knowledge flag')
parser.add_argument('--bots_per_user', type=int, default=6, help='Bots per user')
parser.add_argument('--SIMULATION_EFs_PATH', type=str, default="data/EFs_by_GPT35.csv", help='Simulation EFs path')
parser.add_argument('--favorite_topic_method', type=str, default="review", help='Favorite topic method')

# Advanced Projects' Features
parser.add_argument('--agent', type=str, default="modelbasedRL", help='Agent type')
parser.add_argument('--force_train', type=str2bool, default=True, help='Force training of environment')
parser.add_argument('--output_dim', type=int, default=2, help='Output dimension')
parser.add_argument('--offline_simulation_size', type=int, default=0,
                    help='Offline simulation set size (in No. of users)')
parser.add_argument('--OFFLINE_SIM_DATA_PATH', type=str, default="data/LLM_games_personas.csv", help='LLM data path')
parser.add_argument('--personas_balanced', type=str2bool, default=True, help='Personas balanced flag')
parser.add_argument('--personas_group_number', type=int, default=-1, help='Personas group number')

# Our Project:
#   1. We want to use information from previous games as well when training the transformer, instead of having a cold
#   start for each game.
#   2. We want to "get the best of both worlds" by combining different types of embeddings.

parser.add_argument('--save_previous_games', type=str2bool, default=False, help='Save previous games flag')
parser.add_argument('--combine_features', type=str2bool, default=False, help='Combine features flag')
parser.add_argument('--feature_combination', type=lambda x: x.split('_'), default='EFs_GPT4', help='Feature combination')
parser.add_argument('--pca_dim', type=int, default=36, help='PCA dimension')

parser.add_argument('--final_change', type=str, default="none",
                    help=("Final change of project. 1: Combine features, 2: Save previous games, none: nothing."))


args = parser.parse_args()

main_run = wandb.init(project='Strategy_Transfer_TACL')
config = wandb.config

args = vars(args)

if args["final_change"] == "1":  # Set hyperparameters for change 1: Combine EFs and GPT4
    args["combine_features"] = True
    args["feature_combination"] = ["EFs", "GPT4"]
    args["pca_dim"] = 36

elif args["final_change"] == "2":  # Set hyperparameters for change 2: Save previous games and make architecture
    # transformer.
    args["save_previous_games"] = True
    args["architecture"] = "transformer"

elif args["final_change"] != "none":
    raise ValueError("Only 2 changes. Please choose 'none', '1', or '2'.")

config.update(args)





meta_features_map = {"features": {"EFs": {"FEATURES_PATH": config["SIMULATION_EFs_PATH"], "REVIEW_DIM": 37},
                                  "GPT4": {"FEATURES_PATH": "data/GPT4_PCA_36.csv", "REVIEW_DIM": 36},
                                  "BERT": {"FEATURES_PATH": "data/BERT_PCA_36.csv", "REVIEW_DIM": 36}},
                     "architecture": {"LSTM": {"use_user_vector": True},
                                      "transformer": {"use_user_vector": False}}
                     }

# data = OfflineDataSet(user_groups="X", weight_type=config['loss_weight_type'], config=config)

for meta_feature, meta_feature_map in meta_features_map.items():
    if meta_feature == "features" and config['combine_features']:  # OUR IMPROVEMENT
        for feature_type in config['feature_combination']:  # feature_type = EFs, GPT4, or BERT
            if feature_type not in meta_feature_map.keys():  # feature_type is not one of the legal values
                raise NotImplementedError(feature_type)
            for config_feature, val in meta_feature_map[feature_type].items():
                if config_feature in config.keys():
                    config[config_feature][feature_type] = val
                else:
                    config[config_feature] = {feature_type: val}

    else:  # ORIGINAL CODE
        if config[meta_feature] not in meta_feature_map.keys():
            raise NotImplementedError(meta_feature)
        for config_feature, val in meta_feature_map[config[meta_feature]].items():
            config[config_feature] = val

if "LLM_USERS_PER_PERSONA" in config.keys():
    assert "offline_simulation_size" not in config.keys()
    groups = personas.get_personas_in_group(config.personas_group_number)
    config["offline_simulation_size"] = config["LLM_USERS_PER_PERSONA"] * len(groups)

if "online_simulation_factor" in config.keys():
    config["online_simulation_size"] = (config["offline_simulation_size"] + config["human_train_size"]) * config["online_simulation_factor"]

if config['combine_features']:  # OUR IMPROVEMENT
    config["input_dim"] = config['pca_dim'] + STRATEGY_DIM
else:  # ORIGINAL
    config["input_dim"] = config['REVIEW_DIM'] + STRATEGY_DIM
config["wandb_run_id"] = wandb.run.id



set_global_seed(config["seed"])

all_user_points = []
all_bot_points = []
# hotels = utils.Hotels(config)  # do we use this?

env_name = config["wandb_run_id"]


if config["architecture"] == "LSTM":
    env_model = environments.LSTM_env.LSTM_env(env_name, config=config)
elif config["architecture"] == "transformer":
    env_model = environments.transformer_env.transformer_env(env_name, config=config)
