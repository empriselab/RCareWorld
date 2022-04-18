set scene_name=2t7WUuJeko7
python extract_instance.py %scene_name%
python obj2ply.py %scene_name%
blender --background --python combine2fbx.py -- %scene_name%/%scene_name%/individual_objects_ply %scene_name%/%scene_name%/%scene_name%.fbx