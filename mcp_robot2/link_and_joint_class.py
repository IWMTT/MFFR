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
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mcp_robot2")

class Link:
    def __init__(self, 
                 link_name: str,
                 link_geometry: cq.Workplane|None, 
                 joint_xyz: np.ndarray = np.zeros(3), 
                 joint_rpy: np.ndarray = np.zeros(3),
                 geometry_xyz: np.ndarray = np.zeros(3),
                 geometry_rpy: np.ndarray = np.zeros(3),
                 mass:float = 1.0,
                 filename:str = "",
                 inertia_vector:np.ndarray = np.zeros(6)
                    ):
        self.link_name = link_name
        self.link_geometry = link_geometry
        # joint_xyz, joint_rpyのどちらも3次元の配列でなければならない
        self.joint_xyz = joint_xyz
        self.joint_rpy = joint_rpy
        self.geometry_xyz = geometry_xyz
        self.geometry_rpy = geometry_rpy
        self.mass = mass
        self.filename = filename
        self.inertia_vector = inertia_vector
        self.validate()

    def validate(self):
        if not isinstance(self.joint_xyz, np.ndarray) or self.joint_xyz.shape != (3,):
            raise ValueError("joint_xyz must be a 3-element numpy array.")
        if not isinstance(self.joint_rpy, np.ndarray) or self.joint_rpy.shape != (3,):
            raise ValueError("joint_rpy must be a 3-element numpy array.")
        if not isinstance(self.geometry_xyz, np.ndarray) or self.geometry_xyz.shape != (3,):
            raise ValueError("geometry_xyz must be a 3-element numpy array.")
        if not isinstance(self.geometry_rpy, np.ndarray) or self.geometry_rpy.shape != (3,):
            raise ValueError("geometry_rpy must be a 3-element numpy array.")
        print("Link validation passed.")

    def gen_mesh_file(self, filename: str=None, targetdir: str=".") -> None:
        """Generate a mesh file for the link."""

        targetdir = targetdir.rstrip("/")
        if self.link_geometry is None:
            # print("Link geometry is not defined. Skipped.")
            return
        if filename is None:
            filename = f"{targetdir}/mesh/{self.link_name}.stl"
            # if there is no directory, create it
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            cq.exporters.export(self.link_geometry, filename)
            self.filename = f"mesh/{self.link_name}.stl"
            # print(f"Mesh file generated: {filename}")
        # else:
        #     print(f"Mesh file already exists: {filename}. Skipped.")

    def get_link_description(self) -> str:
        """Get the description of the link."""
        ret_description = ''
        if self.link_name == "world":
            ret_description += f'\t<link name="{self.link_name}"/>\n'
            return ret_description
        ret_description += f'\t<link name="{self.link_name}">\n'
        if self.link_geometry is not None:
            ret_description += '\t\t<visual>\n'
            ret_description += '\t\t\t<geometry>\n'
            ret_description += f'\t\t\t\t<mesh filename="{self.filename}"/>\n'
            ret_description += '\t\t\t</geometry>\n'
            ret_description += '\t\t</visual>\n'
            ret_description += '\t\t<collision>\n'
            ret_description += '\t\t\t<geometry>\n'
            ret_description += f'\t\t\t\t<mesh filename="{self.filename}"/>\n'
            ret_description += '\t\t\t</geometry>\n'
            ret_description += '\t\t</collision>\n'
        ret_description += '\t\t<inertial>\n'
        ret_description += f'\t\t\t<mass value="{self.mass}"/>\n'
        ret_description += f'\t\t\t<inertia ixx="{self.inertia_vector[0]}" ixy="{self.inertia_vector[1]}" ixz="{self.inertia_vector[2]}" iyy="{self.inertia_vector[3]}" iyz="{self.inertia_vector[4]}" izz="{self.inertia_vector[5]}"/>\n'
        ret_description += '\t\t</inertial>\n'
        ret_description += '\t</link>\n'
        
        return ret_description

class JointType(Enum):
    revolute = "revolute"
    continuous = "continuous"
    prismatic = "prismatic"
    fixed = "fixed"
    floating = "floating"
    planar = "planar"
    UNKNOWN = "unknown"

class Joint:
    def __init__(self, joint_name: str, 
                 joint_type: JointType, 
                 parent_link: Link, 
                 child_link: Link,
                 axis_xyz: np.ndarray = np.array([0,0,1]),
                 origin_xyz: np.ndarray = None,
                 origin_rpy: np.ndarray = None,
                 lower_limit: float = -math.pi,
                 upper_limit: float = math.pi,
                 velocity_limit: float = 1.0,
                 effort_limit: float = 100.0,
                 damping: float = 0.0,
                 friction: float = 0.0):
        self.joint_name = joint_name
        self.joint_type = joint_type
        self.parent_link = parent_link
        self.child_link = child_link
        self.axis_xyz = axis_xyz
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit
        self.velocity_limit = velocity_limit
        self.effort_limit = effort_limit
        self.damping = damping
        self.friction = friction
        
        if origin_xyz is None:
            self.origin_xyz = parent_link.joint_xyz
        else:
            self.origin_xyz = origin_xyz

        if origin_rpy is None:
            self.origin_rpy = parent_link.joint_rpy
        else:
            self.origin_rpy = origin_rpy
        self.validate()

    def validate(self):
        if not isinstance(self.axis_xyz, np.ndarray) or self.axis_xyz.shape != (3,):
            raise ValueError("axis_xyz must be a 3-element numpy array.")
        if not isinstance(self.lower_limit, float):
            raise ValueError("lower_limit must be a float.")
        if not isinstance(self.upper_limit, float):
            raise ValueError("upper_limit must be a float.")
        if not isinstance(self.velocity_limit, float):
            raise ValueError("velocity_limit must be a float.")
        if not isinstance(self.effort_limit, float):
            raise ValueError("effort_limit must be a float.")
        # print("Joint validation passed.")

    def get_joint_description(self) -> str:
        """Get the description of the joint."""
        ret_description = ''
        ret_description += f'\t<joint name="{self.joint_name}" type="{self.joint_type.value}">\n'
        ret_description += f'\t\t<parent link="{self.parent_link.link_name}"/>\n'
        ret_description += f'\t\t<child link="{self.child_link.link_name}"/>\n'
        ret_description += '\t\t<origin xyz="{} {} {}" rpy="{} {} {}"/>\n'.format(*self.origin_xyz, *self.origin_rpy)
        ret_description += '\t\t<axis xyz="{} {} {}"/>\n'.format(*self.axis_xyz)
        ret_description += f'\t\t<limit effort="{self.effort_limit}" lower="{self.lower_limit}" upper="{self.upper_limit}" velocity="{self.velocity_limit}"/>\n'
        ret_description += f'\t\t<dynamics damping="{self.damping}" friction="{self.friction}"/>\n'
        ret_description += '\t</joint>\n'
        
        return ret_description
    
    def get_joint_description_srdf(self) -> str:
        """Get the description of the joint in SRDF format."""
        return f'\t\t<joint name="{self.joint_name}">\n'


def xyz_axes(vector_xyz: np.ndarray = np.zeros(3),vector_rpy: np.ndarray = np.zeros(3)):
    """X, Y, Z軸を表示する関数"""
    # 赤: X軸、緑: Y軸、青: Z軸
    axis_length = 1  # 円柱の長さ
    axis_radius = 0.1  # 円柱の半径
    _x = vector_xyz[0]
    _y = vector_xyz[1]
    _z = vector_xyz[2]


    # X axis
    x_axis = Workplane("YZ").circle(axis_radius).extrude(axis_length).translate(tuple(vector_xyz))

    x_axis = x_axis.rotate((_x, _y, _z), (_x+1, _y, _z), math.degrees(vector_rpy[0])).rotate((_x, _y, _z), (_x, _y+1, _z), math.degrees(vector_rpy[1])).rotate((_x, _y, _z), (_x, _y, _z+1), math.degrees(vector_rpy[2]))

    # Y axis
    y_axis = Workplane("ZX").circle(axis_radius).extrude(axis_length).translate(tuple(vector_xyz))
    y_axis = y_axis.rotate((_x, _y, _z), (_x+1, _y, _z), math.degrees(vector_rpy[0])).rotate((_x, _y, _z), (_x, _y+1, _z), math.degrees(vector_rpy[1])).rotate((_x, _y, _z), (_x, _y, _z+1), math.degrees(vector_rpy[2]))

    # Z axis
    z_axis = Workplane("XY").circle(axis_radius).extrude(axis_length).translate(tuple(vector_xyz))
    z_axis = z_axis.rotate((_x, _y, _z), (_x+1, _y, _z), math.degrees(vector_rpy[0])).rotate((_x, _y, _z), (_x, _y+1, _z), math.degrees(vector_rpy[1])).rotate((_x, _y, _z), (_x, _y, _z+1), math.degrees(vector_rpy[2]))

    asm = cq.Assembly()
    asm.add(x_axis, name="X", color=cq.Color(1, 0, 0))  # 赤
    asm.add(y_axis, name="Y", color=cq.Color(0, 1, 0))  # 緑
    asm.add(z_axis, name="Z", color=cq.Color(0, 0, 1))  # 青

    return asm


def gen_link(link_name: str, cylinder_length: float, cylinder_diameter: float, elbow_size: float, elbow_diameter: float, angle: float = 0.0) -> Link:
    """
    Generate a link based on the type provided.

    Args:
        cylinder_length: length of the cylinder, which is an element of the link
        cylinder_diameter: diameter of the cylinder, which is an element of the link
        elbow_size: size of the elbow, which is an element of the link connecting the adjucent link
        elbow_diameter: diameter of the elbow, which is an element of the link connecting the adjucent link
        angle: angle of the elbow (deg) , default is 0.0

    Returns:
        object: The generated link object.
    """


    # Create the elbow
    elbow_torus = torus(elbow_size, elbow_diameter)
    filter_box = box(elbow_size, elbow_size, elbow_size).translate((elbow_size/2,elbow_size/2, -elbow_size/2))
    elbow = elbow_torus * filter_box
    elbow = elbow.rotate((0, 0, 0), (1, 0, 0), 90).translate((-elbow_size/2, 0, cylinder_length)).rotate((0, 0, 0), (0, 0, 1), 180)  # Rotate the elbow to align it with the cylinder
    elbow = elbow.rotate((0, 0, 0), (0, 0, 1), angle)  # Rotate the elbow by the specified angle
    # Combine the cylinder and elbow
    if cylinder_length > 0:
        # Create the main cylinder
        cylinder = Workplane("XY").circle(cylinder_diameter / 2).extrude(cylinder_length)
        link = cylinder.add(elbow)
    else:
        link = elbow
    
    # calculate the joint position and orientation
    joint_xyz = np.array([elbow_size/2*math.cos(math.radians(angle)), elbow_size/2*math.sin(math.radians(angle)), cylinder_length+elbow_size/2])

    joint_rpy = np.array([0, math.radians(90), math.radians(angle)])  # Assuming the joint is aligned with the elbow angle

    return Link(link_name=link_name, link_geometry=link, joint_xyz=joint_xyz, joint_rpy=joint_rpy, geometry_xyz=np.zeros(3), geometry_rpy=np.zeros(3))

def gen_ee_link(link_name: str, cylinder_length: float, cylinder_diameter: float) -> Link| None:
    """
    Generate an end effector link based on the type provided.

    Args:
        cylinder_length: length of the cylinder, which is an element of the link
        cylinder_diameter: diameter of the cylinder, which is an element of the link

    Returns:
        object: The generated end effector link object.
    """
    if cylinder_length > 0:
        # Create the main cylinder
        cylinder = Workplane("XY").circle(cylinder_diameter / 2).extrude(cylinder_length)
        link = cylinder
    else:
        return None
        
    # calculate the joint position and orientation
    joint_xyz = np.array([0, 0, cylinder_length/2])
    joint_rpy = np.array([0, 0, 0])  # Assuming the joint is aligned with the elbow angle

    return Link(link_name=link_name, link_geometry=link, joint_xyz=joint_xyz, joint_rpy=joint_rpy, geometry_xyz=np.zeros(3), geometry_rpy=np.zeros(3))


    return gen_link(link_name, cylinder_length, cylinder_diameter, elbow_size, elbow_diameter, angle)

@mcp.tool()
async def update_robot(list_of_length=[3, 3, 3]) -> None:
    """
    Update the telbot type to the telbot type based on given link lengths.

    Args:
        list_of_length: List of lengths.
    """
    if list_of_length is None or len(list_of_length) != 3:
        print("Invalid list_of_length. It should be a list of three lengths.")
        mcp.error("Invalid list_of_length. It should be a list of three lengths.")
        return

    # Delete the existing mesh directory if it exists
    if os.path.exists("mesh"):
        import shutil
        shutil.rmtree("mesh")


    robot_description = '<?xml version="1.0" ?>\n<robot name="test_robot">\n'
    robot_description += Link("world", None).get_link_description()


    srdf_description = '<?xml version="1.0" ?>\n'
    srdf_description += '<robot name="test_robot">\n'
    srdf_description += '\t<group name="arm">\n'

    base_link = gen_link("base_link", list_of_length[0], 3, 3, 3, 0)
    base_link.gen_mesh_file()
    robot_description += Joint("world_joint", JointType.fixed, Link("world", None), base_link).get_joint_description()
    robot_description += base_link.get_link_description()
    srdf_description += Joint("world_joint", JointType.fixed, Link("world", None), base_link).get_joint_description_srdf()

    links = [base_link]

    for i in range(len(list_of_length)):
        if i == 0: # Skip base link
            continue
        link_a = gen_link(f"link_{2*i-1}", 0, 3, 3, 3, 180)
        link_a.gen_mesh_file()
        links.append(link_a)
        robot_description += link_a.get_link_description()
        joint_previous_to_link_a = Joint(f"joint_{2*i-1}", JointType.revolute, links[2*i-2], link_a)
        robot_description += joint_previous_to_link_a.get_joint_description()
        srdf_description += joint_previous_to_link_a.get_joint_description_srdf()

        link_b = gen_link(f"link_{2*i}", list_of_length[i], 3, 3, 3, 0)
        link_b.gen_mesh_file()
        links.append(link_b)
        robot_description += link_b.get_link_description()
        joint_previous_to_link_b = Joint(f"joint_{2*i}", JointType.revolute, link_a, link_b)
        robot_description += joint_previous_to_link_b.get_joint_description()
        srdf_description += joint_previous_to_link_b.get_joint_description_srdf()

    link_7 = gen_link(f"link_{2*len(list_of_length)+1}", 0, 3, 3, 3, 180)
    link_7.gen_mesh_file()
    links.append(link_7)
    robot_description += link_7.get_link_description()
    joint_previous_to_link_7 = Joint(f"joint_{2*len(list_of_length)+1}", JointType.revolute, links[-2], link_7)
    robot_description += joint_previous_to_link_7.get_joint_description()
    srdf_description += joint_previous_to_link_7.get_joint_description_srdf()

    link_ee = gen_ee_link(f"link_{2*len(list_of_length)+2}", 3, 2)
    link_ee.gen_mesh_file()
    links.append(link_ee)
    robot_description += link_ee.get_link_description()
    joint_previous_to_link_ee = Joint(f"joint_{2*len(list_of_length)+2}", JointType.revolute, links[-2], link_ee)
    robot_description += joint_previous_to_link_ee.get_joint_description()
    srdf_description += joint_previous_to_link_ee.get_joint_description_srdf()



    robot_description += '</robot>'

    srdf_description += '\t</group>\n'
    srdf_description += f'\t<end_effector name="eef" parent_link="{links[-1].link_name}" group="arm"/>\n'
    srdf_description += '\t<virtual_joint name="virtual_joint" type="fixed" parent_frame="world" child_link="base_link"/>\n'

    for i in range(len(links) - 1):
        srdf_description += f'\t<disable_collisions link1="{links[i].link_name}" link2="{links[i+1].link_name}" reason="Adjacent"/>\n'

    srdf_description += '</robot>'

    # Save the descriptions to files
    with open('test_robot.urdf', 'w') as f:
        f.write(robot_description)
    with open('test_robot.srdf', 'w') as f:
        f.write(srdf_description)



def test():
    # ./meshディレクトリを削除
    if os.path.exists("mesh"):
        import shutil
        shutil.rmtree("mesh")


 
    """Test function to generate and display a link."""
    robot_description = '<?xml version="1.0" ?>\n<robot name="test_robot">\n'
    robot_description += Link("world", None).get_link_description()

    srdf_description = '<?xml version="1.0" ?>\n'
    srdf_description += '<robot name="test_robot">\n'
    srdf_description += '\t<group name="arm">\n'

    base_link = gen_link("base_link", 10, 3, 3, 3, 0)
    base_link.gen_mesh_file()

    robot_description += Joint("world_joint", JointType.fixed, Link("world", None), base_link).get_joint_description()
    robot_description += base_link.get_link_description()
    srdf_description += Joint("world_joint", JointType.fixed, Link("world", None), base_link).get_joint_description_srdf()

    link_1 = gen_link("link_1", 0, 2, 3, 3, 180)
    link_1.gen_mesh_file()

    robot_description += link_1.get_link_description()
    robot_description += Joint("joint_0", JointType.revolute, base_link, link_1).get_joint_description()
    srdf_description += Joint("joint_0", JointType.revolute, base_link, link_1).get_joint_description_srdf()

    link_2 = gen_link("link_2", 5, 2, 3, 3, 0)
    link_2.gen_mesh_file()

    robot_description += link_2.get_link_description()
    robot_description += Joint("joint_1", JointType.revolute, link_1, link_2).get_joint_description()
    srdf_description += Joint("joint_1", JointType.revolute, link_1, link_2).get_joint_description_srdf()

    link_3 = gen_link("link_3", 0, 2, 3, 3, 180)
    link_3.gen_mesh_file()

    robot_description += link_3.get_link_description()
    robot_description += Joint("joint_2", JointType.revolute, link_2, link_3).get_joint_description()
    srdf_description += Joint("joint_2", JointType.revolute, link_2, link_3).get_joint_description_srdf()

    link_4 = gen_link("link_4", 3, 2, 3, 3, 0)
    link_4.gen_mesh_file()

    robot_description += link_4.get_link_description()
    robot_description += Joint("joint_3", JointType.revolute, link_3, link_4).get_joint_description()
    srdf_description += Joint("joint_3", JointType.revolute, link_3, link_4).get_joint_description_srdf()

    link_5 = gen_link("link_5", 0, 2, 3, 3, 180)
    link_5.gen_mesh_file()

    robot_description += link_5.get_link_description()
    robot_description += Joint("joint_4", JointType.revolute, link_4, link_5).get_joint_description()
    srdf_description += Joint("joint_4", JointType.revolute, link_4, link_5).get_joint_description_srdf()

    link_6 = gen_link("link_6", 3, 2, 3, 3, 0)
    link_6.gen_mesh_file()

    robot_description += link_6.get_link_description()
    robot_description += Joint("joint_5", JointType.revolute, link_5, link_6).get_joint_description()
    srdf_description += Joint("joint_5", JointType.revolute, link_5, link_6).get_joint_description_srdf()


    robot_description += '</robot>'

    srdf_description += '\t</group>\n'
    srdf_description += f'\t<end_effector name="eef" parent_link="{link_6.link_name}" group="arm"/>\n'
    srdf_description += '\t<virtual_joint name="virtual_joint" type="fixed" parent_frame="world" child_link="base_link"/>\n'
    srdf_description += f'\t<disable_collisions link1="{link_1.link_name}" link2="{link_2.link_name}" reason="Adjacent"/>\n'
    srdf_description += f'\t<disable_collisions link1="{link_2.link_name}" link2="{link_3.link_name}" reason="Adjacent"/>\n'
    srdf_description += f'\t<disable_collisions link1="{link_3.link_name}" link2="{link_4.link_name}" reason="Adjacent"/>\n'
    srdf_description += f'\t<disable_collisions link1="{link_4.link_name}" link2="{link_5.link_name}" reason="Adjacent"/>\n'
    srdf_description += f'\t<disable_collisions link1="{link_5.link_name}" link2="{link_6.link_name}" reason="Adjacent"/>\n'
    srdf_description += '</robot>'
    print(robot_description)
    # Save the descriptions to files
    with open('test_robot.urdf', 'w') as f:
        f.write(robot_description)
    with open('test_robot.srdf', 'w') as f:
        f.write(srdf_description)

    return robot_description , srdf_description


# urdf, srdf = test()
# # descriptionをファイルに保存する
# with open('test_robot.urdf', 'w') as f:
#     f.write(urdf)
# with open('test_robot.srdf', 'w') as f:
#     f.write(srdf)
if __name__ == "__main__":
    test()
    # Initialize and run the server
    mcp.run(transport='stdio')