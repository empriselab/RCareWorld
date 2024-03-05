import bpy
import sys
import os


def find_max_group(weights):
    max_weight = 0
    max_index = 0
    for i in range(len(weights)):
        item = weights[i]
        if item > max_weight:
            max_weight = item
            max_index = i
    return max_index


def extractVertexGroup(from_path, to_path, hier_path):
    to_dir = "/".join(to_path.split("/")[:-1])
    res_dir = "/".join(hier_path.split("/")[:-1])
    if not os.path.exists(to_dir):
        os.makedirs(to_dir)
    if not os.path.exists(res_dir):
        os.makedirs(res_dir)

    objs = bpy.data.objects
    objs.remove(objs["Cube"], do_unlink=True)
    objs.remove(objs["Camera"], do_unlink=True)
    objs.remove(objs["Light"], do_unlink=True)

    bpy.ops.import_scene.fbx(filepath=from_path)
    print(bpy.data.armatures.keys())
    real_armature = bpy.data.armatures["SMPLX-female"]
    print(real_armature.bones.keys())

    with open(hier_path, "w") as f:
        for key in real_armature.bones.keys():
            if real_armature.bones[key].parent is None:
                f.write(key + " None 0\n")
            elif real_armature.bones[key].parent.name.find("root") != -1:
                f.write(key + " " + real_armature.bones[key].parent.name + " 0\n")
            else:
                f.write(key + " " + real_armature.bones[key].parent.name + " 1\n")

    bpy.ops.export_scene.obj(
        filepath=to_path, keep_vertex_order=True, use_vertex_groups=True
    )


argv = sys.argv
argv = argv[argv.index("--") + 1 :]

extractVertexGroup(argv[0], argv[1], argv[2])
