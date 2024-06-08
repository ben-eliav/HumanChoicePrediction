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
    "name": "Recreates results for original transformer.",
    "method": "grid",
    "metric": {
        "goal": "maximize",
        "name": "ENV_Test_accuracy_per_mean_user_and_bot"
    },
    "parameters": {
        "seed": {"values": list(range(3))},
        "architecture": {"values": ["transformer"]},    
    },
    "command": command
}

# Initialize a new sweep
sweep_id = wandb.sweep(sweep=sweep_config, project=project)
print("run this line to run your agent in a screen:")
print(f"screen -dmS \"sweep_agent\" wandb agent {YOUR_WANDB_USERNAME}/{project}/{sweep_id}")