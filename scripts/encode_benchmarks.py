from io import StringIO
import math
import os
import sys

def load_dtp(filename):
    TimePoints  = []
    Constraints = []
    W = 1

    with open(filename,"r") as tnfile:
        f = StringIO(tnfile.read())

    [N, M] = f.readline().strip().split()
    N = int(N)
    M = int(M)
    for i in range(0,N):
        [X, T] = f.readline().strip().split()
        assert (T == "c")
        TimePoints.append(X)
    for i in range(0,M):
        line = f.readline().strip().split()
        D = int(line[0])
        Constraints.append([])
        assert (line[1] == "f")
        for j in range(1,D+1):
            # 4*(j-1) + 2 = 4*j - 2
            # 4*(j-1) + 6 = 4*j + 2
            (X,Y,l,u) = tuple(line[4*j-2: 4*j+2])
            if l == "-inf":
                l = -math.inf
            else:
                l = int(l)
                W = max(W, abs(l))
            if u == "+inf":
                u = math.inf
            else:
                u = int(u)
                W = max(W, abs(u))
            Constraints[-1].append((Y,X,l,u))
            assert l <= u
        assert len(Constraints[-1]) == D

    assert len(TimePoints)  == N
    assert len(Constraints) == M

    return TimePoints, Constraints, W*N

def encode_minizinc_SAT(TimePoints, Constraints, H):
    mzn = StringIO()
    NameMap = dict()

    for X in TimePoints:
        NameMap[X] = len(NameMap)+1

    mzn.write("array[1..{}] of var 0..{}: X;\n".format(len(NameMap), H))

    for disj in Constraints:
        atoms = []
        for (Y,X,l,u) in disj:
            assert l != -math.inf or u != math.inf
            tmp = []
            if l != -math.inf:
                tmp.append("X[{Y}] - X[{X}] >= {l}".format(Y=NameMap[Y],X=NameMap[X],l=l))
            if u != math.inf:
                tmp.append("X[{Y}] - X[{X}] <= {u}".format(Y=NameMap[Y],X=NameMap[X],u=u))
            atoms.append("({})".format(" /\ ".join(tmp)))
        mzn.write("constraint {};\n".format(" \/ ".join(atoms)))

    mzn.write("output[\"(sat)\"];\n")
    mzn.write("solve satisfy;")

    return mzn.getvalue()

def relax_instance(input_file, variable_heuristic, value_heuristic):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    constraint_count = sum(1 for line in lines if line.startswith('constraint'))

    new_lines = [f'array[1..{constraint_count}] of var 0..1: V;\n']

    v_index = 1
    for line in lines:
        if line.startswith('constraint'):
            new_line = f'constraint V[{v_index}] = 1 - ({line.strip()[11:].rstrip(";")});\n'
            new_lines.append(new_line)
            v_index += 1
        else:
            if not line.startswith('solve') and not line.startswith('output'):
                new_lines.append(line)
                new_lines.append('\n')

    new_lines.append('\n')
    new_lines.append('var int: obj = sum(V);\n')
    new_lines.append(f'solve :: int_search(X, {variable_heuristic}, {value_heuristic}) minimize obj;\n')
    new_lines.append('\n')

    new_lines.append('output [show(obj)]')

    result = ''.join(new_lines)
    return result

def write_to_file(fileName, content):
    with open(fileName, "w") as f:
        f.write(content)

def create_output_folder_structure(input_folder, output_folder):
    """
    Recreate the same folder structure from input_folder under output_folder.
    """
    for dirpath, dirnames, filenames in os.walk(input_folder):
        structure = os.path.join(output_folder, os.path.relpath(dirpath, input_folder))
        if not os.path.isdir(structure):
            os.makedirs(structure)

def encode_files_from_folder(input_folder, output_folder, encoding_type, heuristic, sat_path):
    for filename in os.listdir(input_folder):
        timePoints, constraints, H = load_dtp(input_folder + "/" + filename)

        if encoding_type == "sat":
            minizincSatFile = encode_minizinc_SAT(timePoints, constraints, H)
            write_to_file(output_folder + "/" + filename + ".mzn", minizincSatFile)
        elif encoding_type == "relaxed":
            minizincRelaxedFile = relax_instance(sat_path + "/" + filename + ".mzn", heuristic, "indomain_min")
            write_to_file(output_folder + "/" + filename + ".mzn", minizincRelaxedFile)

def run(filtered_benchmarks_path):
    root_folder = "encoded_benchmarks"
    solvers = ["chuffed", "gecode"]
    encoding_types = ["sat", "relaxed"]
    heuristics = ["max-regret", "first-fail"]

    for solver in solvers:
        for encoding_type in encoding_types:
            for heuristic in heuristics:
                path = os.path.join(root_folder, solver, encoding_type, heuristic)
                os.makedirs(path, exist_ok=True)
                
                create_output_folder_structure(filtered_benchmarks_path, path)

                for subdir in os.listdir(filtered_benchmarks_path):
                    sat_path = os.path.join(root_folder, solver, "sat", heuristic, subdir)

                    subdir_path = os.path.join(filtered_benchmarks_path, subdir)
                    output_path = os.path.join(path, subdir)
                    print(output_path)
                    encode_files_from_folder(subdir_path, output_path, encoding_type, heuristic, sat_path)

def run(filtered_benchmarks_path):
    root_folder = "encoded_benchmarks"
    solvers = ["chuffed", "gecode"]
    encoding_types = ["sat", "relaxed"]
    heuristics = ["max_regret", "first_fail"]

    for solver in solvers:
        for encoding_type in encoding_types:
            if encoding_type == "sat":
                path = os.path.join(root_folder, solver, encoding_type)
                os.makedirs(path, exist_ok=True)

                create_output_folder_structure(filtered_benchmarks_path, path)

                for subdir in os.listdir(filtered_benchmarks_path):
                    sat_path = os.path.join(root_folder, solver, "sat", subdir)

                    subdir_path = os.path.join(filtered_benchmarks_path, subdir)
                    output_path = os.path.join(path, subdir)
                    print(output_path)
                    encode_files_from_folder(subdir_path, output_path, encoding_type, "no heuristic", sat_path)
            else:
                for heuristic in heuristics:
                    path = os.path.join(root_folder, solver, encoding_type, heuristic)
                    os.makedirs(path, exist_ok=True)

                    create_output_folder_structure(filtered_benchmarks_path, path)

                    for subdir in os.listdir(filtered_benchmarks_path):
                        sat_path = os.path.join(root_folder, solver, "sat", subdir)

                        subdir_path = os.path.join(filtered_benchmarks_path, subdir)
                        output_path = os.path.join(path, subdir)
                        print(output_path)
                        encode_files_from_folder(subdir_path, output_path, encoding_type, heuristic, sat_path)


if len(sys.argv) != 2:
    print("Usage: python encode_benchmarks.py folder_path_to_encode")
else:
    run(sys.argv[1])