import pymeshlab
import os
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_dir", type=str, default="smpl_stl")
    parser.add_argument("-o", "--output_dir", type=str, default="smpl_parts")
    args = parser.parse_args()
    input_dir = args.input_dir
    output_dir = args.output_dir

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for item in os.listdir(input_dir):
        if item.split(".")[-1] != "obj":
            continue
        ms = pymeshlab.MeshSet()
        ms.load_new_mesh(input_dir+"/"+item)
        ms.save_current_mesh(output_dir+"/"+item.replace(".obj", ".stl"))