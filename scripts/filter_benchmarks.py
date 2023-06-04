import os
import random
import sys

def run(folder_path, num_files_to_keep=100):
    for dirpath, dirnames, filenames in os.walk(folder_path):
        # Get all files from each subdirectory
        files = [os.path.join(dirpath, f) for f in filenames]

        # Ensure there are more than num_files_to_keep files in the subdirectory
        if len(files) <= num_files_to_keep:
            print(f"There are not more than {num_files_to_keep} files in the subdirectory: {dirpath}. (Number of files: {len(files)})")
            continue

        # Randomly select num_files_to_keep files to keep
        files_to_keep = random.sample(files, num_files_to_keep)

        # Delete all files not in files_to_keep
        for file in files:
            if file not in files_to_keep:
                os.remove(file)
        print(f"Operation completed in {dirpath}. Previously : {len(files)} files. Now : {len(files_to_keep)} files.")


if len(sys.argv) != 2:
    print("Usage: python filter_benchmarks.py folder_path")
else:
    run(sys.argv[1])
