from pyntcloud import PyntCloud
import numpy as np
import pandas as pd
import os
import argparse

def parse_line(line_items, rule):
    temp = {}
    for idx, item in enumerate(rule):
        temp[item]=line_items[idx+1]
    return temp


def parse_house_file(path):
    H = []
    L = []
    R = []
    S = []
    V = []
    P = []
    C = []
    O = []
    E = []
    last_label = ""
    with open(path) as f:
        for line in f:
            line = line.strip().replace("  ", " ")
            items = line.split(" ")
            if items[0] == "H":
                temp = parse_line(items, ["name", "label", "#images", "#panoramas", "#vertices", "#surfaces", "#segments", "#objects", "#categories", "#regions", "#portals", "#levels", "nd1", "nd2", "nd3", "nd4", "nd5","xlo", "ylo", "zlo", "xhi", "yhi", "zhi"])
                H.append(temp)
                last_label = "H"
            if items[0] == "L":
                temp = parse_line(items, ["level_index", "#regions", "label", "px", "py", "pz", "xlo", "ylo", "zlo", "xhi", "yhi", "zhi"])
                L.append(temp)
                last_label = "L"
            if items[0] == 'R':
                temp = parse_line(items, ["region_index", "level_index", "nd1", "nd2", "label", "px", "py", "pz", "xlo", "ylo", "zlo", "xhi", "yhi", "zhi", "height"])
                R.append(temp)
                last_label = "R"
            if items[0] == "S":
                temp = parse_line(items, ["surface_index", "region_index", "nd1", "label", "px", "py", "pz", "nx", "ny","nz", "xlo", "ylo", "zlo", "xhi", "yhi", "zhi"])
                S.append(temp)
                last_label = "S"
            if items[0] == "V":
                temp = parse_line(items, ["vertex_index", "surface_index", "label", "px", "py", "pz", "nx", "ny", "nz"])
                V.append(temp)
                last_label = "V"
            if items[0] == "P" and last_label != "R":
                temp = parse_line(items, ["name", "panorama_index", "region_index", "nd", "px", "py", "pz"])
                P.append(temp)
            if items[0] == "C":
                temp = parse_line(items, ["category_index", "category_mapping_index", "category_mapping_name", "mpcat40_index", "mpcat40_name"])
                C.append(temp)
            if items[0] == "O":
                temp = parse_line(items, ["object_index", "region_index", "category_index", "px", "py", "pz", "a0x", "a0y", "a0z", "a1x", "a1y", "a1z", "r0", "r1", "r2"])
                O.append(temp)
            if items[0] == "E":
                temp = parse_line(items, ["segment_index", "object_index", "id", "area", "px", "py", "pz", "xlo", "ylo", "zlo", "xhi", "yhi", "zhi"])
                E.append(temp)
    return H, L, R, S, V, P, C, O, E


def write_to_obj(path, points, faces, color=True, normal=False, normals=None):
    with open(path, "w") as f:
        for i in range(points.shape[0]):
            item = points[i]
            f.write("v ")
            for j in range(6 if color else 3):
                f.write(str(item[j])+" ")
            f.write("\n")
            if normal:
                n = normals[i]
                f.write("vn ")
                for j in range(3):
                    f.write(str(n[j])+" ")
                f.write("\n")
        
        for item in faces:
            f.write("f ")
            for i in range(3):
                if normal:
                    f.write(str(item[i])+"//"+str(item[i])+" ")
                else:
                    f.write(str(item[i])+"// ")
            f.write("\n")

def parse_category_mapping_tsv(path):
    mapping = {}
    all_mapping = pd.read_table(path)
    index = all_mapping['index']
    cat = all_mapping['mpcat40']

    for i in range(index.shape[0]):
        mapping[index[i]] = cat[i]
    return mapping


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("scene_id", type=str, default="1LXtFkjw3qL")
    args = parser.parse_args()

    scene_id = args.scene_id

    house_file = "{}/{}/house_segmentations/{}.house".format(scene_id, scene_id, scene_id)
    model_file = "{}/{}/house_segmentations/{}.ply".format(scene_id, scene_id, scene_id)
    obj_save_dir = "{}/{}/individual_objects".format(scene_id, scene_id)
    if not os.path.exists(obj_save_dir):
        os.makedirs(obj_save_dir)

    category_mapping = parse_category_mapping_tsv("category_mapping.tsv")
    category_mapping[-1] = "minus1"
    
    #H, L, R, S, V, P, C, O, E = parse_house_file(house_file)

    #house_model = o3d.io.read_triangle_mesh(model_file)
    cloud = PyntCloud.from_file(model_file)
    
    category_ids = np.asarray(cloud.mesh['category_id'])
    
    segment_ids = np.asarray(cloud.mesh['segment_id'])
    segment_ids_index = np.unique(segment_ids)

    # face
    f1s = np.asarray(cloud.mesh['v1'])
    f2s = np.asarray(cloud.mesh['v2'])
    f3s = np.asarray(cloud.mesh['v3'])

    # points
    v1s = np.asarray(cloud.points['x'])
    v2s = np.asarray(cloud.points['y'])
    v3s = np.asarray(cloud.points['z'])
    nv1s = np.asarray(cloud.points['nx'])
    nv2s = np.asarray(cloud.points['ny'])
    nv3s = np.asarray(cloud.points['nz'])
    rs = np.asarray(cloud.points['red'])
    gs = np.asarray(cloud.points['green'])
    bs = np.asarray(cloud.points['blue'])

    obj_counter = {}
    for segment_id in segment_ids_index: # for each object_instance
        segment_index_mapping = (segment_ids == segment_id)
        cat = np.unique(category_ids[segment_index_mapping])
        if len(cat) > 1:
            print("warning category:", cat)

        final_cat = cat[0]
        print("cat:", category_mapping[final_cat])
        try:
            obj_counter[category_mapping[final_cat]] += 1
        except KeyError:
            obj_counter[category_mapping[final_cat]] = 1
        
        obj_name = category_mapping[final_cat] + "_" + str(obj_counter[category_mapping[final_cat]])

        v1_mapping = f1s[segment_index_mapping]
        v2_mapping = f2s[segment_index_mapping]
        v3_mapping = f3s[segment_index_mapping]

        # reorder face index for new object
        v_index = np.hstack((v1_mapping, v2_mapping)) # concateneta all the vertices index of segment
        v_index = np.hstack((v_index, v3_mapping))
        new_to_old_v_mapping = np.unique(v_index) # find all the vertices index

        new_points = np.zeros((new_to_old_v_mapping.shape[0], 6))
        new_points_normal = np.zeros((new_to_old_v_mapping.shape[0], 3))
        face_dict = {}
        for i, f_i in enumerate(new_to_old_v_mapping):
            old_v_index = new_to_old_v_mapping[i]
            new_points[i][0] = v1s[old_v_index]
            new_points[i][1] = v2s[old_v_index]
            new_points[i][2] = v3s[old_v_index]
            new_points[i][3] = rs[old_v_index]/255
            new_points[i][4] = gs[old_v_index]/255
            new_points[i][5] = bs[old_v_index]/255
            new_points_normal[i][0] = nv1s[old_v_index]
            new_points_normal[i][1] = nv2s[old_v_index]
            new_points_normal[i][2] = nv2s[old_v_index]
            face_dict[old_v_index] = i + 1

        new_faces = np.zeros((v1_mapping.shape[0], 3), dtype=int)
        for j in range(v1_mapping.shape[0]):
            new_faces[j][0] = face_dict[v1_mapping[j]]
            new_faces[j][1] = face_dict[v2_mapping[j]]
            new_faces[j][2] = face_dict[v3_mapping[j]]

        write_to_obj(obj_save_dir+"/"+obj_name+".obj", new_points, new_faces, normal=True, normals=new_points_normal)


    