import cadquery as cq
from cadquery.vis import show
from cadquery import Workplane
from cadquery import *
from cadquery.func import *
import math
from enum import Enum
from typing import Any
import numpy as np
import os
from link_and_joint_class import *
from snake_link import *

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mcp_robot2")


def template_of_snake_robot():
    """
    Update the telbot type to the telbot type based on given link lengths.

    Args:
        list_of_length: List of lengths.
    """

    # Delete the existing mesh directory if it exists
    if os.path.exists("mesh"):
        import shutil
        shutil.rmtree("mesh")


    robot_description = '<?xml version="1.0" ?>\n<robot name="test_robot">\n'
    robot_description += Link("world", None).get_link_description()


    srdf_description = '<?xml version="1.0" ?>\n'
    srdf_description += '<robot name="test_robot">\n'
    srdf_description += '\t<group name="arm">\n'

    base_link = gen_base_rail_link(link_name = "base_link", rail_length=10.0, rail_width=1.0, rail_size=0.1, origin_xyz=np.zeros(3), origin_rpy=np.zeros(3), joint_xyz=None, joint_rpy=None )
    base_link.gen_mesh_file()
    joint_world_to_base = Joint("world_joint", JointType.fixed, Link("world", None), base_link)
    robot_description += joint_world_to_base.get_joint_description()
    robot_description += base_link.get_link_description()
    srdf_description += joint_world_to_base.get_joint_description_srdf()

    links = [base_link]

    link_01 = gen_horizontal_link( link_name="link_01", link_length=1.0, link_width=0.7, link_height=0.375*2, root_joint_structure=False, tip_joint_structure="Clevis", body_shape="box")
    link_01.gen_mesh_file()
    joint_01 = Joint("joint_01", JointType.prismatic, base_link, link_01, origin_xyz=np.array([0, 0, 0.375]), axis_xyz=np.array([0, 1, 0]))
    robot_description += joint_01.get_joint_description()
    robot_description += link_01.get_link_description()
    srdf_description += joint_01.get_joint_description_srdf()
    links.append(link_01)

    link_02 = gen_horizontal_link( link_name="link_02", link_length=1.41, link_width=0.7, link_height=0.375*2, root_joint_structure="tang", tip_joint_structure="Clevis", body_shape="box")
    link_02.gen_mesh_file()
    joint_02 = Joint("joint_02", JointType.revolute, link_01, link_02)
    robot_description += joint_02.get_joint_description()
    robot_description += link_02.get_link_description()
    srdf_description += joint_02.get_joint_description_srdf()
    links.append(link_02)

    link_03 = gen_horizontal_link( link_name="link_03", link_length=1.13, link_width=0.7, link_height=0.375*2, root_joint_structure="tang", tip_joint_structure=False, body_shape="box")
    link_03.gen_mesh_file()
    joint_03 = Joint("joint_03", JointType.revolute, link_02, link_03)
    robot_description += joint_03.get_joint_description()
    robot_description += link_03.get_link_description()
    srdf_description += joint_03.get_joint_description_srdf()
    links.append(link_03)

    link_04 = gen_gimbal_link2(link_name="link_04", cylinder1_radius=0.435*2, cylinder1_length=0.11, cylinder2_offset_y=0.565257, cylinder2_offset_z=0.356751, cylinder2_radius=0.87, cylinder2_width=0.88, joint_structure="tang")
    link_04.gen_mesh_file()
    joint_04 = Joint("joint_04", JointType.revolute, link_03, link_04, axis_xyz=np.array([0, 1, 0]))
    robot_description += joint_04.get_joint_description()
    robot_description += link_04.get_link_description()
    srdf_description += joint_04.get_joint_description_srdf()
    links.append(link_04)

    link_05 = gen_gimbal_link2(link_name="link_05", cylinder1_radius=0, cylinder1_length=0, cylinder2_offset_y=0.86, cylinder2_offset_z=0.39, cylinder2_radius=0.9, cylinder2_width=0.9, joint_structure="clevis", reverse=True)
    link_05.gen_mesh_file()
    joint_05 = Joint("joint_05", JointType.revolute, link_04, link_05, axis_xyz=np.array([1, 0, 0]),origin_rpy=np.array([0, 0, math.pi]))
    robot_description += joint_05.get_joint_description()
    robot_description += link_05.get_link_description()
    srdf_description += joint_05.get_joint_description_srdf()
    links.append(link_05)

    link_06 = gen_horizontal_link( link_name="link_06", link_length=1.175, link_width=0.7, link_height=0.26*2, root_joint_structure=False, tip_joint_structure="tang", body_shape="box")
    link_06.gen_mesh_file()
    joint_06 = Joint("joint_06", JointType.revolute, link_05, link_06, axis_xyz=np.array([0, 1, 0]))
    robot_description += joint_06.get_joint_description()
    robot_description += link_06.get_link_description()
    srdf_description += joint_06.get_joint_description_srdf()
    links.append(link_06)

    link_07 = gen_horizontal_link( link_name="link_07", link_length=0.62, link_width=0.48, link_height=0.44, root_joint_structure="Clevis", tip_joint_structure=False, body_shape="box")
    link_07.gen_mesh_file()
    joint_07 = Joint("joint_07", JointType.revolute, link_06, link_07)
    robot_description += joint_07.get_joint_description()
    robot_description += link_07.get_link_description()
    srdf_description += joint_07.get_joint_description_srdf()
    links.append(link_07)

    link_08 = gen_wrist_link( link_name="link_08", box1_width=0.8, box1_length=0.32, box1_height=0.52, box2_width=0.2, box2_length=1.0, box2_height=0.2, box2_span=0.72, box2_offset_y=0.0, box2_offset_z=0.2, joint_xyz=np.array([0.0, 0.68,0.2]))
    link_08.gen_mesh_file()
    joint_08 = Joint("joint_08", JointType.revolute, link_07, link_08,axis_xyz=np.array([0, 1, 0]))
    robot_description += joint_08.get_joint_description()
    robot_description += link_08.get_link_description()
    srdf_description += joint_08.get_joint_description_srdf()
    links.append(link_08)

    link_09 = gen_simple_cylinder_link(link_name="link_09", link_length=0.8, link_radius=0.26, origin_xyz=np.array([0.0, 0.0, 0.15]))
    link_09.gen_mesh_file()
    joint_09 = Joint("joint_09", JointType.revolute, link_08, link_09,axis_xyz=np.array([1, 0, 0]),origin_rpy=np.array([-math.pi/2, 0, 0]))
    robot_description += joint_09.get_joint_description()
    robot_description += link_09.get_link_description()
    srdf_description += joint_09.get_joint_description_srdf()
    links.append(link_09)

    link_10 = gen_simple_cylinder_link(link_name="link_10", link_length=0.2, link_radius=0.2)
    link_10.gen_mesh_file()
    joint_10 = Joint("joint_10", JointType.revolute, link_09, link_10)
    robot_description += joint_10.get_joint_description()
    robot_description += link_10.get_link_description()
    srdf_description += joint_10.get_joint_description_srdf()
    links.append(link_10)


    robot_description += '</robot>'

    srdf_description += '\t</group>\n'
    srdf_description += f'\t<end_effector name="eef" parent_link="{link_10.link_name}" group="arm"/>\n'
    srdf_description += '\t<virtual_joint name="virtual_joint" type="fixed" parent_frame="world" child_link="base_link"/>\n'
    for i in range(len(links) - 1):
        srdf_description += f'\t<disable_collisions link1="{links[i].link_name}" link2="{links[i+1].link_name}" reason="Adjacent"/>\n'

    srdf_description += '</robot>'
    # print(robot_description)
    # Save the descriptions to files
    with open('test_robot.urdf', 'w') as f:
        f.write(robot_description)
    with open('test_robot.srdf', 'w') as f:
        f.write(srdf_description)

    return robot_description , srdf_description



@mcp.tool()
async def update_snake_robot_link_length(list_of_length=[1.0, 1.41, 1.13,1.175, 0.62]):
    """
    Update the snake robot's link lengths based on the provided list.

    Args:
        list_of_length (list of float): List specifying the length of each link. 
            The order corresponds to each link in the robot arm.
    Returns:
        tuple: (robot_description, srdf_description)
    """

    # Delete the existing mesh directory if it exists
    if os.path.exists("mesh"):
        import shutil
        shutil.rmtree("mesh")


    robot_description = '<?xml version="1.0" ?>\n<robot name="test_robot">\n'
    robot_description += Link("world", None).get_link_description()


    srdf_description = '<?xml version="1.0" ?>\n'
    srdf_description += '<robot name="test_robot">\n'
    srdf_description += '\t<group name="arm">\n'

    base_link = gen_base_rail_link(link_name = "base_link", rail_length=10.0, rail_width=1.0, rail_size=0.1, origin_xyz=np.zeros(3), origin_rpy=np.zeros(3), joint_xyz=None, joint_rpy=None )
    base_link.gen_mesh_file()
    joint_world_to_base = Joint("world_joint", JointType.fixed, Link("world", None), base_link)
    robot_description += joint_world_to_base.get_joint_description()
    robot_description += base_link.get_link_description()
    srdf_description += joint_world_to_base.get_joint_description_srdf()

    links = [base_link]

    link_01 = gen_horizontal_link( link_name="link_01", link_length=list_of_length[0], link_width=0.7, link_height=0.375*2, root_joint_structure=False, tip_joint_structure="Clevis", body_shape="box")
    link_01.gen_mesh_file()
    joint_01 = Joint("joint_01", JointType.prismatic, base_link, link_01, origin_xyz=np.array([0, 0, 0.375]), axis_xyz=np.array([0, 1, 0]))
    robot_description += joint_01.get_joint_description()
    robot_description += link_01.get_link_description()
    srdf_description += joint_01.get_joint_description_srdf()
    links.append(link_01)

    link_02 = gen_horizontal_link( link_name="link_02", link_length=list_of_length[1], link_width=0.7, link_height=0.375*2, root_joint_structure="tang", tip_joint_structure="Clevis", body_shape="box")
    link_02.gen_mesh_file()
    joint_02 = Joint("joint_02", JointType.revolute, link_01, link_02)
    robot_description += joint_02.get_joint_description()
    robot_description += link_02.get_link_description()
    srdf_description += joint_02.get_joint_description_srdf()
    links.append(link_02)

    link_03 = gen_horizontal_link( link_name="link_03", link_length=list_of_length[2], link_width=0.7, link_height=0.375*2, root_joint_structure="tang", tip_joint_structure=False, body_shape="box")
    link_03.gen_mesh_file()
    joint_03 = Joint("joint_03", JointType.revolute, link_02, link_03)
    robot_description += joint_03.get_joint_description()
    robot_description += link_03.get_link_description()
    srdf_description += joint_03.get_joint_description_srdf()
    links.append(link_03)

    link_04 = gen_gimbal_link2(link_name="link_04", cylinder1_radius=0.435*2, cylinder1_length=0.11, cylinder2_offset_y=0.565257, cylinder2_offset_z=0.356751, cylinder2_radius=0.87, cylinder2_width=0.88, joint_structure="tang")
    link_04.gen_mesh_file()
    joint_04 = Joint("joint_04", JointType.revolute, link_03, link_04, axis_xyz=np.array([0, 1, 0]))
    robot_description += joint_04.get_joint_description()
    robot_description += link_04.get_link_description()
    srdf_description += joint_04.get_joint_description_srdf()
    links.append(link_04)

    link_05 = gen_gimbal_link2(link_name="link_05", cylinder1_radius=0, cylinder1_length=0, cylinder2_offset_y=0.86, cylinder2_offset_z=0.39, cylinder2_radius=0.9, cylinder2_width=0.9, joint_structure="clevis", reverse=True)
    link_05.gen_mesh_file()
    joint_05 = Joint("joint_05", JointType.revolute, link_04, link_05, axis_xyz=np.array([1, 0, 0]),origin_rpy=np.array([0, 0, math.pi]))
    robot_description += joint_05.get_joint_description()
    robot_description += link_05.get_link_description()
    srdf_description += joint_05.get_joint_description_srdf()
    links.append(link_05)

    link_06 = gen_horizontal_link( link_name="link_06", link_length=list_of_length[3], link_width=0.7, link_height=0.26*2, root_joint_structure=False, tip_joint_structure="tang", body_shape="box")
    link_06.gen_mesh_file()
    joint_06 = Joint("joint_06", JointType.revolute, link_05, link_06, axis_xyz=np.array([0, 1, 0]))
    robot_description += joint_06.get_joint_description()
    robot_description += link_06.get_link_description()
    srdf_description += joint_06.get_joint_description_srdf()
    links.append(link_06)

    link_07 = gen_horizontal_link( link_name="link_07", link_length=list_of_length[4], link_width=0.48, link_height=0.44, root_joint_structure="Clevis", tip_joint_structure=False, body_shape="box")
    link_07.gen_mesh_file()
    joint_07 = Joint("joint_07", JointType.revolute, link_06, link_07)
    robot_description += joint_07.get_joint_description()
    robot_description += link_07.get_link_description()
    srdf_description += joint_07.get_joint_description_srdf()
    links.append(link_07)

    link_08 = gen_wrist_link( link_name="link_08", box1_width=0.8, box1_length=0.32, box1_height=0.52, box2_width=0.2, box2_length=1.0, box2_height=0.2, box2_span=0.72, box2_offset_y=0.0, box2_offset_z=0.2, joint_xyz=np.array([0.0, 0.68,0.2]))
    link_08.gen_mesh_file()
    joint_08 = Joint("joint_08", JointType.revolute, link_07, link_08,axis_xyz=np.array([0, 1, 0]))
    robot_description += joint_08.get_joint_description()
    robot_description += link_08.get_link_description()
    srdf_description += joint_08.get_joint_description_srdf()
    links.append(link_08)

    link_09 = gen_simple_cylinder_link(link_name="link_09", link_length=0.8, link_radius=0.26, origin_xyz=np.array([0.0, 0.0, 0.15]))
    link_09.gen_mesh_file()
    joint_09 = Joint("joint_09", JointType.revolute, link_08, link_09,axis_xyz=np.array([1, 0, 0]),origin_rpy=np.array([-math.pi/2, 0, 0]))
    robot_description += joint_09.get_joint_description()
    robot_description += link_09.get_link_description()
    srdf_description += joint_09.get_joint_description_srdf()
    links.append(link_09)

    link_10 = gen_simple_cylinder_link(link_name="link_10", link_length=0.2, link_radius=0.2)
    link_10.gen_mesh_file()
    joint_10 = Joint("joint_10", JointType.revolute, link_09, link_10)
    robot_description += joint_10.get_joint_description()
    robot_description += link_10.get_link_description()
    srdf_description += joint_10.get_joint_description_srdf()
    links.append(link_10)


    robot_description += '</robot>'

    srdf_description += '\t</group>\n'
    srdf_description += f'\t<end_effector name="eef" parent_link="{link_10.link_name}" group="arm"/>\n'
    srdf_description += '\t<virtual_joint name="virtual_joint" type="fixed" parent_frame="world" child_link="base_link"/>\n'
    for i in range(len(links) - 1):
        srdf_description += f'\t<disable_collisions link1="{links[i].link_name}" link2="{links[i+1].link_name}" reason="Adjacent"/>\n'

    srdf_description += '</robot>'
    # print(robot_description)
    # Save the descriptions to files
    with open('test_robot.urdf', 'w') as f:
        f.write(robot_description)
    with open('test_robot.srdf', 'w') as f:
        f.write(srdf_description)

    return 

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')