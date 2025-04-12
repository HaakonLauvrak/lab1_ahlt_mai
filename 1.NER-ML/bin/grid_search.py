#!/usr/bin/env python3

import os
import csv
import re
import time
import itertools
from datetime import datetime
from collections import defaultdict

import itertools

# Define parameter spaces for each model
param_spaces = {
    "CRF": {
        "algorithm": ["lbfgs", "l2sgd", "ap", "pa", "arow"],
        "feature.minfreq": ["3", "5", "7"],
        "c1": ["0.05", "0.1", "0.2"],
        "c2": ["0.1", "0.3", "0.5"],
        "max_iterations": ["50", "100", "200"],
        "epsilon": ["0.00001", "0.0001"]
    },
    "MEM": {
        "C": [0.1, 1.0, 10.0],  # Now using actual numbers, not strings
        "solver": ["lbfgs", "newton-cg", "liblinear", "sag"],
        "max_iter": [100, 500, 1000],  # Now using actual integers
    },
    "SVM": {
        "C": [0.1, 1.0, 10.0],  # Now using actual numbers, not strings
        "kernel": ["linear", "poly", "rbf"],
        "degree": [2, 3],  # Now using actual integers
        "gamma": [0.01, 0.1, 1.0]  # Now using actual numbers
    }
}

# Function to generate parameter combinations
def generate_parameter_combinations(model_type, max_combinations=None):
    params = param_spaces[model_type]
    
    # For CRF, we need to handle algorithm-specific parameters
    if model_type == "CRF":
        all_combinations = []
        
        # For lbfgs algorithm
        lbfgs_params = {k: v for k, v in params.items() if k != "algorithm"}
        lbfgs_keys = list(lbfgs_params.keys())
        lbfgs_values = [lbfgs_params[k] for k in lbfgs_keys]
        
        for values in itertools.product(*lbfgs_values):
            param_dict = {"algorithm": "lbfgs"}
            param_dict.update(dict(zip(lbfgs_keys, values)))
            all_combinations.append(param_dict)
        
        # For l2sgd algorithm (doesn't use epsilon)
        l2sgd_params = {k: v for k, v in params.items() if k != "algorithm" and k != "epsilon"}
        l2sgd_keys = list(l2sgd_params.keys())
        l2sgd_values = [l2sgd_params[k] for k in l2sgd_keys]
        
        for values in itertools.product(*l2sgd_values):
            param_dict = {"algorithm": "l2sgd"}
            param_dict.update(dict(zip(l2sgd_keys, values)))
            all_combinations.append(param_dict)
            
        # For other algorithms
        for alg in ["ap", "pa", "arow"]:
            other_params = {k: v for k, v in params.items() if k != "algorithm" and k != "c1" and k != "c2"}
            other_keys = list(other_params.keys())
            other_values = [other_params[k] for k in other_keys]
            
            for values in itertools.product(*other_values):
                param_dict = {"algorithm": alg}
                param_dict.update(dict(zip(other_keys, values)))
                all_combinations.append(param_dict)
    else:
        # For MEM and SVM, we can generate all combinations
        keys = list(params.keys())
        values = [params[k] for k in keys]
        
        all_combinations = []
        for vals in itertools.product(*values):
            all_combinations.append(dict(zip(keys, vals)))
    
    # Limit combinations if specified
    if max_combinations and len(all_combinations) > max_combinations:
        print(f"Limiting from {len(all_combinations)} to {max_combinations} combinations for {model_type}")
        all_combinations = all_combinations[:max_combinations]
    
    return all_combinations

# Function to convert parameter dictionary to command string
def params_to_string(params):
    return " ".join([f"{k}={v}" for k, v in params.items()])

# Function to extract F1 macro average from stats file
def extract_f1_score(model_type):
    stats_file = f"1.NER-ML\\results\\devel-{model_type}.stats"
    
    try:
        with open(stats_file, 'r') as f:
            content = f.read()
            
            # Look for the M.avg line and extract the F1 score
            match = re.search(r"M\.avg\s+[-]\s+[-]\s+[-]\s+[-]\s+[-]\s+[\d.]+%\s+[\d.]+%\s+([\d.]+)%", content)
            if match:
                return float(match.group(1))
            else:
                print(f"Could not find M.avg F1 score in {stats_file}")
                return None
    except FileNotFoundError:
        print(f"Stats file not found: {stats_file}")
        return None

def main():
    print("Select models to test:")
    print("1. CRF")
    print("2. MEM")
    print("3. SVM")
    print("4. All")
    
    choice = input("Enter your choice (1-4): ")
    
    models = []
    if choice == "1":
        models = ["CRF"]
    elif choice == "2":
        models = ["MEM"]
    elif choice == "3":
        models = ["SVM"]
    elif choice == "4":
        models = ["CRF", "MEM", "SVM"]
    else:
        print("Invalid choice")
        return
    
    # Ask for max combinations limit
    max_combinations = None
    try:
        limit_input = input("Enter maximum number of parameter combinations to test per model (or press Enter for no limit): ")
        if limit_input.strip():
            max_combinations = int(limit_input)
    except ValueError:
        print("Invalid input for max combinations, proceeding with no limit")
    
    # Create results file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"grid_search_results_{timestamp}.csv"
    
    with open(results_file, 'w', newline='') as csvfile:
        fieldnames = ['model_type', 'params', 'f1_score']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for model in models:
            print(f"\n{'='*50}")
            print(f"Running tests for {model}")
            print(f"{'='*50}")
            
            # Generate parameter combinations for this model
            param_combinations = generate_parameter_combinations(model, max_combinations)
            total_combinations = len(param_combinations)
            
            print(f"Testing {total_combinations} parameter combinations for {model}")
            
            for i, param_dict in enumerate(param_combinations):
                print(f"\nRunning combination {i+1}/{total_combinations} for {model}:")
                print(f"Parameters: {param_dict}")
                
                # Build the command string based on model type
                param_str = params_to_string(param_dict)
                
                # Special handling for MEM model
                if model == "MEM":
                    # Create a custom Python script to run MEM with the correct parameter types
                    temp_script = f"mem_run_{timestamp}_{i}.py"
                    with open(temp_script, 'w') as f:
                        f.write("""
import sys
import os

# Get directory of this script
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get path to NER directory
ner_dir = os.path.join(current_dir, "1.NER-ML")
bin_dir = os.path.join(ner_dir, "bin")

# Add bin directory to path so we can import modules
sys.path.append(bin_dir)

from train import train
from predict import predict

# Parameters with correct types
params = {
""")
                        for k, v in param_dict.items():
                            if k == "max_iter" or k == "n_jobs":
                                # These need to be integers
                                f.write(f"    '{k}': {v},\n")
                            elif k == "C":
                                # This needs to be a float
                                f.write(f"    '{k}': {v},\n")
                            else:
                                # Others can be strings
                                f.write(f"    '{k}': '{v}',\n")
                        f.write("}\n\n")
                        
                        f.write("""
# Train the model
train(os.path.join(ner_dir, "preprocessed", "train.feat"), 
      params,
      os.path.join(ner_dir, "models", "model.mem"))

# Predict using the model
predict(os.path.join(ner_dir, "preprocessed", "devel.feat"),
        os.path.join(ner_dir, "models", "model.mem"),
        os.path.join(ner_dir, "results", "devel-MEM.out"))
""")
                    
                    # Run the custom script
                    cmd = f"python {temp_script}"
                    print(f"Executing custom MEM script: {cmd}")
                    exit_code = os.system(cmd)
                    
                    # Clean up the temporary script
                    try:
                        os.remove(temp_script)
                    except:
                        pass
                    
                else:
                    # For CRF and SVM, use the regular command
                    cmd = f"python 1.NER-ML\\bin\\run.py train predict {model} {param_str}"
                    print(f"Executing: {cmd}")
                    exit_code = os.system(cmd)
                
                if exit_code == 0:
                    print("Command executed successfully")
                    
                    # Wait a moment for files to be written
                    time.sleep(1)
                    
                    # Extract F1 score
                    f1_score = extract_f1_score(model)
                    
                    # Save result
                    result = {
                        'model_type': model,
                        'params': str(param_dict),
                        'f1_score': f1_score if f1_score is not None else "ERROR"
                    }
                    
                    writer.writerow(result)
                    csvfile.flush()  # Ensure data is written to disk
                    
                    print(f"F1 Score: {f1_score}")
                else:
                    print(f"Command failed with exit code {exit_code}")
    
    print(f"\nGrid search completed. Results saved to {results_file}")
    
    # Find best parameters
    best_params = {}
    with open(results_file, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            model = row['model_type']
            if row['f1_score'] != "ERROR":
                try:
                    f1 = float(row['f1_score'])
                    if model not in best_params or f1 > best_params[model]['f1']:
                        best_params[model] = {
                            'params': row['params'],
                            'f1': f1
                        }
                except ValueError:
                    print(f"Could not convert F1 score to float: {row['f1_score']}")
    
    print("\nBest parameters for each model:")
    for model, result in best_params.items():
        print(f"{model}: F1 = {result['f1']}, Parameters = {result['params']}")

if __name__ == "__main__":
    main()