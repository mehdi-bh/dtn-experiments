import subprocess
import time
import sys

if len(sys.argv) < 4:
    print("Usage: python wrapper.py <mzn_file> <output_file> <solver>")
    sys.exit(1)

mzn_file = sys.argv[1]
output_file = sys.argv[2]
solver = sys.argv[3]

command = f"minizinc --solver {solver} --all-solutions {mzn_file}"

process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

start_time = time.time() * 1000

with open(output_file, 'w') as f:
    for line in process.stdout:
        if not (line.startswith("-") or line.startswith("=") or line.startswith("%")):
            solving_time = round((time.time() * 1000) - start_time, 2)

            # print(f'{solving_time}, {line.strip()}\n')
            f.write(f'{solving_time}, {line.strip()}\n')
            f.flush()

# Wait for the process to finish and get the return code
return_code = process.wait()
