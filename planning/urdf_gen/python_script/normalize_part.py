import os
import argparse
import numpy as np


def parse_obj(obj_name):
    vertex_data = []
    flines = []
    with open(obj_name) as f:
        for line in f:
            if line.startswith("v "):  # it is vertex line
                head, x, y, z = line.strip().split(" ")
                vertex_data.append([float(x), float(y), float(z)])
            if line.startswith("f"):
                flines.append(line)
    return np.array(vertex_data), flines


def get_center(vertex):
    return np.mean(vertex, axis=0)


def write_obj(path, vertex, faces):
    with open(path, "w") as f:
        for item in vertex:
            f.write(
                "v " + str(item[0]) + " " + str(item[1]) + " " + str(item[2]) + "\n"
            )
        for line in faces:
            f.write(line)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_dir", type=str, default="smpl_stl")
    parser.add_argument("-o", "--output_dir", type=str, default="smpl_parts")
    parser.add_argument("--offset_path", type=str)
    args = parser.parse_args()

    input_dir = args.input_dir
    part_list = os.listdir(input_dir)
    write_dir = args.output_dir

    if not os.path.exists(write_dir):
        os.makedirs(write_dir)

    with open(args.offset_path, "w") as f:
        for part in part_list:
            vertex, faces = parse_obj(input_dir + "/" + part)
            center = get_center(vertex)
            f.write(
                part
                + " "
                + str(center[0])
                + " "
                + str(center[1])
                + " "
                + str(center[2])
                + "\n"
            )
            vertex -= center
            write_obj(write_dir + "/" + part, vertex, faces)
