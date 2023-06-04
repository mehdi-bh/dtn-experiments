import subprocess
import sys
  
if len(sys.argv) < 7:
    print("Usage: python wrapper_java.py <minicp_solver_path> <input_file> <output_file> <relaxation> <variable> <value>")
    sys.exit(1)

minicp_solver_path = sys.argv[1]
input_file = sys.argv[2]
output_file = sys.argv[3]
relaxation = sys.argv[4]
variable = sys.argv[5]
value = sys.argv[6]

command = f"java -jar {minicp_solver_path} {input_file} {relaxation} {variable} {value}"

process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

with open(output_file, 'w') as f:
    for line in process.stdout:
        f.write(line)
        f.flush()

# Wait for the process to finish and get the return code
return_code = process.wait()
