import argparse
import numpy as np

def process_a_base(f, link_name, xyz, rpy, inertial=None):
    f.write('   <link name="{}">\n'.format(link_name))
    f.write('       <inertial>\n')
    f.write('           <origin xyz="{} {} {}" rpy="{} {} {}" />\n'.format(xyz[0], xyz[1], xyz[2], rpy[0], rpy[1], rpy[2]))
    f.write('           <mass value="0" />\n')
    if inertial is None:
        f.write('           <inertia ixx="0" ixy="0" ixz="0" iyy="0" iyz="0" izz="0" />\n')  
    else:
        f.write('           <inertia ixx="{}" ixy="{}" ixz="{}" iyy="{}" iyz="{}" izz="{}" />\n'.format(inertial[0],inertial[1],inertial[2], inertial[3], inertial[4],inertial[5]))
    f.write('       </inertial></link>\n') 

def process_a_link(f, link_name, link_path, xyz, rpy, inertial=None, color=None):
    f.write('   <link name="{}">\n'.format(link_name))
    f.write('       <inertial>\n')
    f.write('           <origin xyz="{} {} {}" rpy="{} {} {}" />\n'.format(xyz[0], xyz[1], xyz[2], rpy[0], rpy[1], rpy[2]))
    f.write('           <mass value="1" />\n')
    if inertial is None:
        f.write('           <inertia ixx="0" ixy="0" ixz="0" iyy="0" iyz="0" izz="0" />\n')  
    else:
        f.write('           <inertia ixx="{}" ixy="{}" ixz="{}" iyy="{}" iyz="{}" izz="{}" />\n'.format(inertial[0],inertial[1],inertial[2], inertial[3], inertial[4],inertial[5]))
    f.write('       </inertial>\n')  
    f.write('       <visual>\n')
    f.write('           <origin xyz="{} {} {}" rpy="{} {} {}" />\n'.format(xyz[0], xyz[1], xyz[2], rpy[0], rpy[1], rpy[2]))
    f.write('           <geometry><mesh filename="{}" /></geometry>\n'.format(link_path))
    if color is None:
        f.write('           <material name=""><color rgba="0.827450980392157 0.83921568627451 0.827450980392157 1" /></material>\n')
    else:
        f.write('           <material name=""><color rgba="{} {} {} 1" /></material>\n'.format(color[0], color[1], color[2]))
    f.write('       </visual>\n')
    f.write('       <collision>\n')
    f.write('           <origin xyz="{} {} {}" rpy="{} {} {}" />\n'.format(xyz[0], xyz[1], xyz[2], rpy[0], rpy[1], rpy[2]))
    f.write('           <geometry><mesh filename="{}" /></geometry>\n'.format(link_path))
    f.write('       </collision></link>\n')

def process_a_1d_joint(f, joint_name, parent, child, xyz, rpy, joint_type="revolute", limits=[0,0,0,0], axis=[0,1,0]):
    f.write('   <joint name="{}" type="{}">\n'.format(joint_name, joint_type))
    f.write('       <origin xyz="{} {} {}" rpy="{} {} {}" />\n'.format(xyz[0], xyz[1], xyz[2], rpy[0], rpy[1], rpy[2]))
    f.write('       <parent link="{}" />\n'.format(parent))
    f.write('       <child link="{}" />\n'.format(child))
    f.write('       <axis xyz="{} {} {}" />\n'.format(axis[0],axis[1], axis[2]))
    f.write('       <limit lower="{}" upper="{}" effort="{}" velocity="{}" />\n'.format(limits[0], limits[1], limits[2], limits[3]))
    f.write('   </joint>\n')

def process_a_3d_joint(f, parent, child, xyz, rpy, limits=None):
    fake_link_name_x = parent+"_"+child+"_rot_link_x"
    fake_link_name_y = parent+"_"+child+"_rot_link_y"
    f.write('   <link name={}></link>\n'.format(fake_link_name_x))
    f.write('   <link name={}></link>\n'.format(fake_link_name_y))
    process_a_1d_joint(f, parent+"_"+child+"_joint_x", parent, fake_link_name_x, [0,0,0], rpy, limits=limits, axis=[1,0,0])
    process_a_1d_joint(f, parent+"_"+child+"_joint_y", fake_link_name_x, fake_link_name_y, [0,0,0], rpy, limits=limits, axis=[0, 1,0])
    process_a_1d_joint(f, parent+"_"+child+"_joint_z",fake_link_name_y, child, xyz, rpy, limits=limits, axis=[0,0,1])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--part_dir", type=str, default="smpl_stl_normal")
    parser.add_argument("-o", "--urdf_name", type=str, default="test.urdf")
    parser.add_argument("-n", "--package_name", type=str, default="smpl_description")
    parser.add_argument("--offset_path", type=str)
    parser.add_argument("--hier_path", type=str)
    args = parser.parse_args()


    urdf_name = args.urdf_name
    part_dir_path = args.part_dir

    part_pos_dict = {}
    with open(args.offset_path) as f:
        for line in f:
            name, x, y, z = line.strip().split(" ")
            part_pos_dict[name.split(".")[0]] = np.array([float(x), float(y), float(z)])

    # for unity
    unity_urdf_name = urdf_name.replace(".urdf", "_for_unity.urdf")
    with open(unity_urdf_name, "w") as f:
        f.write('<robot name="{}">\n'.format(unity_urdf_name.split(".")[0].split("/")[-1]))

        with open(args.hier_path) as f1:
            for line in f1:
                child, parent, _ = line.strip().split(" ")
                if parent == "None":
                    process_a_base(f, child, xyz=[0,0,0], rpy=[0,0,0])
                else:
                    link_path = "package://"+part_dir_path+"/"+child+".stl"
                    process_a_link(f, child, link_path, xyz=[0,0,0], rpy=[0,0,0])
                    if parent.find("root")!=-1:
                        process_a_1d_joint(f, child+"_joint", parent, child, xyz=[0,0,0], rpy=[0,0,0], joint_type="fixed")
                    else:
                        xyz = part_pos_dict[child] - part_pos_dict[parent]
                        process_a_1d_joint(f, child+"_joint", parent, child, xyz=xyz, rpy=[0,0,0], limits=[0,np.pi,0,0])

        f.write("</robot>\n")
    
    # for moveit
    moveit_urdf_name = urdf_name.replace(".urdf", "_for_moveit.urdf")
    with open(moveit_urdf_name, "w") as f:
        f.write('<robot name="{}">\n'.format(moveit_urdf_name.split(".")[0].split("/")[-1]))

        with open(args.hier_path) as f1:
            for line in f1:
                child, parent, level = line.strip().split(" ")
                if parent == "None":
                    process_a_base(f, child, xyz=[0,0,0], rpy=[0,0,0])
                else:
                    link_path = "package://"+args.package_name+"/"+part_dir_path+"/"+child+".stl"
                    process_a_link(f, child, link_path, xyz=[0,0,0], rpy=[0,0,0])
                    if level == "0":
                        if parent.find("root")!=-1:
                            process_a_1d_joint(f, child+"_joint", parent, child, xyz=[0,0,0], rpy=[0,0,0], joint_type="fixed")
                        else:
                            xyz = part_pos_dict[child] - part_pos_dict[parent]
                            process_a_1d_joint(f, child+"_joint", parent, child, xyz=xyz, rpy=[0,0,0], limits=[0,np.pi,0,0])
                    else:
                        xyz = part_pos_dict[child] - part_pos_dict[parent]
                        process_a_3d_joint(f, parent, child, xyz=xyz, rpy=[0,0,0], limits=[0, np.pi, 0, 0])

        f.write("</robot>\n")