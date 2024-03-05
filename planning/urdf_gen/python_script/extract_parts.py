import numpy as np
import argparse
import os


def parse_obj_with_group(obj_name):
    vlines = []
    vnlines = []
    glines = {}
    with open(obj_name) as f:
        for line in f:
            if line.startswith("v "):  # it is vertex line
                vlines.append(line)
            if line.startswith("vn "):  # it is normal line
                vnlines.append(line)
            if line.startswith("g"):
                g_name = line.strip().split(" ")[-1]
                try:
                    print(g_name, len(glines[g_name]))
                except KeyError:
                    glines[g_name] = []
                    g_label = g_name
            if line.startswith("f"):
                glines[g_name].append(line)
    return vlines, vnlines, glines


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("object_name", type=str)
    parser.add_argument("-o", "--output_dir", type=str, default="smpl_parts")
    parser.add_argument("--hier", type=str)
    args = parser.parse_args()
    # obj_name = "SMPL_f_unityDoubleBlends_lbs_10_scale5_207_v1.0.0.obj"
    # obj_name = "SMPL_f_unityDoubleBlends_lbs_10_scale5_207_v1.0.0_groups.obj"
    obj_name = args.object_name

    output_dir = args.output_dir

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    hier_path = args.hier
    hier_dict = {}
    co_vertex_dict = {}
    with open(hier_path) as f:
        for line in f:
            child, parent, _ = line.strip().split()
            if parent != "None" and parent != "f_avg_root":
                hier_dict[child] = parent

    vlines, vnlines, glines = parse_obj_with_group(obj_name)
    all_counter = 0
    face_id_group_mapping = {}
    part_v_seq_new_index_mapping = {}
    for part_name in glines.keys():  # for each part
        v_seq = []
        vn_seq = []
        for line in glines[part_name]:
            head, face1, face2, face3 = line.strip().split()
            v1i, vt1i, vn1i = face1.split("/")
            v2i, vt2i, vn2i = face2.split("/")
            v3i, vt3i, vn3i = face3.split("/")
            v_seq.append([int(v1i), int(v2i), int(v3i)])
            vn_seq.append([int(vn1i), int(vn2i), int(vn3i)])

        v_seq_unique = np.unique(v_seq)
        vn_seq_unique = np.unique(vn_seq)

        face_id_group_mapping[part_name] = set(v_seq_unique)

        v_seq_new_index_mapping = {}
        vn_seq_new_index_mapping = {}
        for i in range(len(v_seq_unique)):
            v_seq_new_index_mapping[v_seq_unique[i]] = i + 1
        for i in range(len(vn_seq_unique)):
            vn_seq_new_index_mapping[vn_seq_unique[i]] = i + 1
        part_v_seq_new_index_mapping[part_name] = v_seq_new_index_mapping

        with open(output_dir + "/" + part_name + ".obj", "w") as fout:
            for vi in v_seq_unique:
                fout.write(vlines[vi - 1])
            for vni in vn_seq_unique:
                fout.write(vnlines[vni - 1])
            for line in glines[part_name]:
                head, face1, face2, face3 = line.strip().split()
                v1i, vt1i, vn1i = face1.split("/")
                v2i, vt2i, vn2i = face2.split("/")
                v3i, vt3i, vn3i = face3.split("/")
                new_v1i = v_seq_new_index_mapping[int(v1i)]
                new_v2i = v_seq_new_index_mapping[int(v2i)]
                new_v3i = v_seq_new_index_mapping[int(v3i)]
                new_vn1i = vn_seq_new_index_mapping[int(vn1i)]
                new_vn2i = vn_seq_new_index_mapping[int(vn2i)]
                new_vn3i = vn_seq_new_index_mapping[int(vn3i)]
                fout.write(
                    head
                    + " "
                    + str(new_v1i)
                    + "//"
                    + str(new_vn1i)
                    + " "
                    + str(new_v2i)
                    + "//"
                    + str(new_vn2i)
                    + " "
                    + str(new_v3i)
                    + "//"
                    + str(new_vn3i)
                    + "\n"
                )

    with open(hier_path.replace("hier", "covertex"), "w") as f:
        for key in hier_dict.keys():
            intersect_ids = face_id_group_mapping[key].intersection(
                face_id_group_mapping[hier_dict[key]]
            )
            selected_id = int(list(intersect_ids)[0])
            current_child = int(part_v_seq_new_index_mapping[key][selected_id])
            current_parent = int(
                part_v_seq_new_index_mapping[hier_dict[key]][selected_id]
            )
            f.write(
                key
                + " "
                + hier_dict[key]
                + " "
                + str(selected_id)
                + " "
                + str(current_child)
                + " "
                + str(current_parent)
                + "\n"
            )
