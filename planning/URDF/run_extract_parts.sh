#!/bin/bash
model_path=female
model_name=female2_c4-c5
urdf_name=female2_c4-c5
mid_output_dir=mid
part_dir=smplx_stl_normal_test
py_script_path=python_script
res_dir=smplx_description

blender --background --python $py_script_path/extract_vertex_group.py -- $model_path/$model_name.fbx $mid_output_dir/$model_name.obj $mid_output_dir/hier.txt
python $py_script_path/extract_parts.py $mid_output_dir/$model_name.obj -o $mid_output_dir/parts --hier $mid_output_dir/hier.txt

blender --background --python $py_script_path/combine2fbx.py -- $mid_output_dir/parts $mid_output_dir/$model_name\_final.fbx $mid_output_dir/hier.txt

python $py_script_path/normalize_part.py -i $mid_output_dir/parts -o $mid_output_dir/parts_obj_normal --offset_path $mid_output_dir/offset.txt
python $py_script_path/obj2stl.py -i $mid_output_dir/parts_obj_normal -o $res_dir/$part_dir

# the -i part_dir path is used for writing in urdf, package://part_dir
python $py_script_path/generate_rough_urdf.py -i $part_dir -o $res_dir/$urdf_name.urdf -n $res_dir --offset_path $mid_output_dir/offset.txt --hier_path $mid_output_dir/hier.txt

python $py_script_path/write_package_info.py -n $res_dir -i $part_dir