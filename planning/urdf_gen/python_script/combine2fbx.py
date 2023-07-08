import bpy
import sys
import os

def combine2fbx(from_path, to_path, hier_file):
    # load all the ply object
    # and combine to a fbx
    # hier file: this object -> parent

    for item in os.listdir(from_path):
        bpy.ops.import_scene.obj(filepath=from_path+"/"+item)

    objs = bpy.data.objects
    objs.remove(objs["Cube"], do_unlink=True)
    objs.remove(objs["Camera"], do_unlink=True)
    objs.remove(objs["Light"], do_unlink=True)

    with open(hier_file) as f:
        for line in f:
            this_object, parent, _ = line.strip().split(" ")
            if parent != "None":
                try:
                    objs[this_object].parent = objs[parent]    
                    objs[this_object].matrix_parent_inverse = objs[parent].matrix_world.inverted()
                except KeyError:
                    print("Warning: Virtual link exists!")
    
    bpy.ops.export_scene.fbx(filepath=to_path)

argv = sys.argv
argv = argv[argv.index("--") + 1:]
print(argv)
combine2fbx(argv[0], argv[1], argv[2])