# Towards Self-Adaptive Embryonic Systems

Code and data accompanying the paper *Towards Self-Adaptive Embryonic Systems* submitted to DISCOLI 2026.

## Files

- `ca_model.py` — Cellular Automata model of the embryonic system
- `exp1exhaustive.py` — Experiment 1: exhaustive parameter search to identify configurations exhibiting bimodal survivability
- `exp1-*.pkl` — Experiment 1 results dataset
- `exp2collapse.py` — Experiment 2: collapse trajectory analysis for borderline configurations
- `exp2-*.pkl` — Experiment 2 results dataset

## Requirements

Python 3.8+

numpy
scipy
matplotlib
tqdm

## Usage

### Running the simulations

Experiment 1 performs an exhaustive parameter search over death rate and spawn rate 
configurations to identify those exhibiting bimodal survivability:

    python exp1exhaustive.py

Experiment 2 performs a granular collapse trajectory analysis for borderline 
configurations at SR=0.7:

    python exp2collapse.py

Both experiments use multiprocessing (10 processes by default) and may take 
significant time to complete. Results are saved as timestamped `.pkl` files.

Pre-computed datasets are provided:
- `exp1-*.pkl` — results from the exhaustive parameter search
- `exp2-*.pkl` — results from the collapse trajectory analysis

### Running the model interactively

An interactive visualisation of the CA model can be enabled by uncommenting 
the code block at the bottom of `ca_model.py`.

## Acknowledgement

This project has received co-funding from the European Union's Digital Europe Programme and the European Cybersecurity Competence Centre under grant agreement no. 1011226821 Eyvör National Coordination Centre for Cybersecurity Iceland and 101127307 Defend Iceland: Nationwide bug bounty platform.
