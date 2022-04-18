import os
import pymeshlab
from tqdm import tqdm
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("scene_id", type=str, default="1LXtFkjw3qL")
    args = parser.parse_args()

    scene_id = args.scene_id
    obj_save_dir = "{}/{}/individual_objects".format(scene_id, scene_id)
    ply_save_dir = "{}/{}/individual_objects_ply".format(scene_id, scene_id)
    if not os.path.exists(ply_save_dir):
        os.makedirs(ply_save_dir)
    
    for obj in tqdm(os.listdir(obj_save_dir)):
        ms = pymeshlab.MeshSet()
        ms.load_new_mesh(obj_save_dir+"/"+obj)
        ms.save_current_mesh(ply_save_dir+"/"+obj.replace(".obj", ".ply"))