import bpy
import sys
import os

def combine2fbx(from_path, to_path):
    # load all the ply object
    # and combine to a fbx
    
    objs = bpy.data.objects
    objs.remove(objs["Cube"], do_unlink=True)
    objs.remove(objs["Camera"], do_unlink=True)
    objs.remove(objs["Light"], do_unlink=True)
    

    for item in os.listdir(from_path):
        bpy.ops.import_mesh.ply(filepath=from_path+"/"+item)

    bpy.ops.export_scene.fbx(filepath=to_path)

argv = sys.argv
argv = argv[argv.index("--") + 1:]

combine2fbx(argv[0], argv[1])