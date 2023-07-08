import argparse
from asyncore import write

def write_packge(res_dir,version, description, email, author, license, buildtool_dep, run_dep):
    with open(res_dir+"/package.xml", "w") as f:
        f.write('<?xml version="1.0"?>\n')
        f.write('<package>\n')
        f.write('<name>{}</name>\n'.format(res_dir))
        f.write('<version>{}</version>\n'.format(version))
        f.write('<description>{}</description>\n'.format(description))
        f.write('<maintainer email="{}">{}</maintainer>\n'.format(email, author))
        f.write('<license>{}</license>\n'.format(license))
        f.write('<author>{}</author>\n'.format(author))
        for item in buildtool_dep:
            f.write('<buildtool_depend>{}</buildtool_depend>\n'.format(item))
        for item in run_dep:
            f.write("<run_depend>{}</run_depend>\n".format(item))
        f.write("</package>\n")

def write_cmake_list(res_dir, part_dir, buildtool_dep):
    with open(res_dir+"/CMakeLists.txt", "w") as f:
        f.write("cmake_minimum_required(VERSION 2.8.3)\n")
        f.write("project({})\n".format(res_dir))

        for item in buildtool_dep:
            f.write("find_package({} REQUIRED)\n".format(item))

        f.write("catkin_package()\n")

        f.write("foreach(dir {})\n".format(part_dir))
        f.write("install(DIRECTORY ${dir}/\n")
        f.write("   DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/${dir})\n")
        f.write(" endforeach(dir)\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", type=str, default="smpl_description")
    parser.add_argument("-i", "--part_dir", type=str)
    parser.add_argument("-v", "--version", type=str, default="0.0.1")
    parser.add_argument("--desc", type=str, default="smpl")
    parser.add_argument("--email", type=str, default="vinjohn@sjtu.edu.cn")
    parser.add_argument("--author", type=str, default="WenqiangXu")
    parser.add_argument("--license", type=str, default="MIT")
    args = parser.parse_args()

    buildtool_dep = ["catkin"]
    run_dep = ["robot_state_publisher","joint_state_publisher","tf2_ros","rviz"]

    write_packge(args.name, args.version, args.desc, args.email, args.author, args.license, buildtool_dep, run_dep)

    write_cmake_list(args.name, args.part_dir, buildtool_dep)