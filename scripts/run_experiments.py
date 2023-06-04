import os
import subprocess
import sys
import time
import pandas as pd

def create_output_folder_structure(input_folder, output_folder):
    """
    Recreate the same folder structure from input_folder under output_folder.
    """
    for dirpath, dirnames, filenames in os.walk(input_folder):
        structure = os.path.join(output_folder, os.path.relpath(dirpath, input_folder))
        if not os.path.isdir(structure):
            os.makedirs(structure)

def run_parallel(benchmark_input_folder, mzn_input_folder, output_folder, timeout_seconds):
    """
    Run all minizinc files in parallel with a timeout and write the output to the output_folder.
    """
    mzn_files = [os.path.join(dirpath, filename)
                 for dirpath, dirnames, filenames in os.walk(mzn_input_folder)
                 for filename in filenames if filename.endswith('.mzn')]
    output_files = [os.path.splitext(os.path.join(output_folder, os.path.relpath(file, mzn_input_folder)))[0] + '.out'
                    for file in mzn_files]

    commands = []
    """for mzn_file, output_file in zip(mzn_files, output_files):
        os.chmod(mzn_file, 0o700)

        if "chuffed" in mzn_file:
            solver = "chuffed"
        elif "gecode" in mzn_file:
            solver = "gecode"
    
        cmd = ['python', 'wrapper.py', mzn_file, output_file, solver]
        commands.append(' '.join(cmd))"""

    benchmark_input_files = [os.path.join(dirpath, filename)
                 for dirpath, dirnames, filenames in os.walk(benchmark_input_folder)
                 for filename in filenames]
    
    variables_heuristics = ["FIRST_FAIL", "MAX_REGRET"]
    value_heuristic = "FIRST_FAIL"

    for variable_heuristic in variables_heuristics:
        for input_file in benchmark_input_files:
            new_folder = "minicp/" + variable_heuristic.lower()
            output_file_minicp = os.path.join(output_folder, input_file.replace(benchmark_input_folder, new_folder)) + ".out"
            output_folder_minicp = os.path.dirname(output_file_minicp)

            if not os.path.isdir(output_folder_minicp):
                os.makedirs(output_folder_minicp)
            
            cmd = ['python', 'wrapper_java.py', "minicp_solver.jar", input_file, output_file_minicp, "BOOLEAN", variable_heuristic, value_heuristic]
            commands.append(' '.join(cmd))
    
    joblog = 'joblog'

    # Run the commands in parallel
    cmd = ['parallel', '--joblog', joblog, '--jobs', "2", '--timeout', str(timeout_seconds), ':::'] + commands
    subprocess.run(cmd, shell=False)

# Path to the directory containing all benchmark files
input_folder = sys.argv[1]

# Path to the directory containing all minizinc files
minizinc_input_folder = sys.argv[2]

# Path to the directory where you want to save the outputs
output_folder =  sys.argv[3]

# Timeout in seconds
timeout_seconds =  sys.argv[4]

# Create output folder structure
create_output_folder_structure(minizinc_input_folder, output_folder)

# Run minizinc in parallel with timeout
run_parallel(input_folder, minizinc_input_folder, output_folder, timeout_seconds)
