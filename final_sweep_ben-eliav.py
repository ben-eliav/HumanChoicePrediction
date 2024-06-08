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
    "name": "Final run for project, recreates the results shown in paper.",
    "method": "grid",
    "metric": {
        "goal": "maximize",
        "name": "ENV_test_accuracy_per_mean_user_and_bot"
    },
    "parameters": {
        "seed": {"values": list(range(5))},
        "final_change": {"values": ["none", "1", "2"]},
    },
    "command": command
}

# Initialize a new sweep
sweep_id = wandb.sweep(sweep=sweep_config, project=project)
print("run this line to run your agent in a screen:")
print(f"screen -dmS \"sweep_agent\" wandb agent {YOUR_WANDB_USERNAME}/{project}/{sweep_id}")
