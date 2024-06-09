# cloning your code from github:
git clone https://github.com/ben-eliav/HumanChoicePrediction.git

cd HumanChoicePrediction
pip install --upgrade wandb

# Your main sweep:
python final_sweep_ben-eliav.py


python original_transformer_sweep.py
python test_combinations_sweep.py

# More runs appear in your report:
# python sweep_1.py
# python sweep_2.py
# python sweep_3.py
