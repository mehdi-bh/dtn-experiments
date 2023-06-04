import os

def count_files_in_directory(directory):
    file_count = 0
    for root, dirs, files in os.walk(directory):
        file_count += len(files)
    return file_count

directory = 'outputMiniCP/minicp/first_fail/dimacs-gc-tcsp'  # replace with your directory
print(f'There are {count_files_in_directory(directory)} files in the directory "{directory}" and its subdirectories.')
