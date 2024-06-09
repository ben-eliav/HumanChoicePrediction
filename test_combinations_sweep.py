import wandb

YOUR_WANDB_USERNAME = "beneliav1"
project = "Strategy_Transfer_TACL"

command = [
        "${ENVIRONMENT_VARIABLE}",
        "${interpreter}",
        "StrategyTransfer.py",
        "${project}",
        "${args}"
    ]

sweep_config = {
    "name": "Finding best feature combinations.",
    "method": "grid",
    "metric": {
        "goal": "maximize",
        "name": "ENV_Test_accuracy_per_mean_user_and_bot"
    },
    "parameters": {
        "seed": {"values": list(range(1,4))},
        "architecture": {"values": ["LSTM"]},
        "hidden_dim": {"values": [32, 64, 128]},
        "combine_features": {"values": [True]},
        "feature_combination": {"values": [["EFs", "GPT4"], ["EFs", "BERT"]]},
        "ENV_LEARNING_RATE": {"values": [0.001, 0.0001, 1e-5]}
    },
    "command": command
}

# Initialize a new sweep
sweep_id = wandb.sweep(sweep=sweep_config, project=project)
print("run this line to run your agent in a screen:")
print(f"screen -dmS \"sweep_agent\" wandb agent {YOUR_WANDB_USERNAME}/{project}/{sweep_id}")