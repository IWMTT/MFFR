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
from link_and_joint_class import *



def make_d_shape(diameter: float, height: float) -> cq.Workplane:
    # 半円と、直径部分の長方形を組み合わせてD字型を作成
    half_circle = Workplane("XY").circle(diameter / 2).extrude(height)
    rectangle = Workplane("XY").rect(diameter, diameter/2).extrude(height).translate((0, -diameter / 4, 0))
    d_shape = half_circle.union(rectangle)
    d_shape = d_shape.translate((0, diameter/2, -height / 2))
    return d_shape


def gen_base_rail_link(
        link_name: str,
        rail_length: float,
        rail_width: float,
        rail_size: float = 0.1,
        origin_xyz: np.ndarray = np.zeros(3),
        origin_rpy: np.ndarray = np.zeros(3),
        joint_xyz: np.ndarray = None,
        joint_rpy: np.ndarray = None
) -> Link:
    # Generate a base rail link
    rail1 = Workplane("XZ").rect(rail_size, rail_size).extrude(rail_length).translate(( rail_width/2, 0,0))
    rail2 = Workplane("XZ").rect(rail_size, rail_size).extrude(rail_length).translate((-rail_width/2, 0,0))

    link_geometry = rail1 + rail2
    link_geometry = link_geometry.translate(tuple(origin_xyz))
    link_geometry = link_geometry.rotate(tuple(origin_xyz), (1, 0, 0), math.degrees(origin_rpy[0])).rotate(tuple(origin_xyz), (0, 1, 0), math.degrees(origin_rpy[1])).rotate(tuple(origin_xyz), (0, 0, 1), math.degrees(origin_rpy[2]))

    if joint_xyz is None:
        joint_xyz = np.zeros(3) + origin_xyz
    if joint_rpy is None:
        joint_rpy = origin_rpy

    return Link(
        link_name="base_rail_link",
        link_geometry=link_geometry,
        joint_xyz=joint_xyz,
        joint_rpy=joint_rpy,
        geometry_xyz=np.zeros(3),
        geometry_rpy=np.zeros(3),
    )

def gen_gimbal_link2(
    link_name: str,
    cylinder1_radius: float,
    cylinder1_length: float,
    cylinder2_offset_y: float,
    cylinder2_offset_z: float,
    cylinder2_radius: float,
    cylinder2_width: float,
    joint_structure: str = "clevis",
    reverse: bool = False
) :
    """
    Generate a gimbal link with a torus and a cylinder.

    Args:
        link_name (str): Name of the link.
        torus_radius (float): Radius of the torus.
        torus_section_radius (float): Radius of the torus section.
        offset_length (float): Length of the offset.
        cylinder_radius (float): Radius of the cylinder.
        cylinder_height (float): Height of the cylinder.
        cylinder_offset_y (float): Y offset for the cylinder.
        cylinder_offset_z (float): Z offset for the cylinder.
        joint_structure (str): Type of joint structure ("clevis" or "tang").
        reverse (bool): If True, reverse the orientation of the link.

    Returns:
        Link: The generated link object.
    """
    # オフセット長さが設定されている場合、それ分の円筒を作成
    if cylinder1_length > 0:
        offset_cylinder = (
            Workplane("XY")
            .center(0, 0)
            .circle(cylinder1_radius/2.0)
            .extrude(cylinder1_length)
        )
        offset_cylinder = offset_cylinder.rotate((0,0,0),(1,0,0),-90)
    else:
        offset_cylinder = cq.Compound.makeCompound([])

    # boxを作成して、斜めに切る
    # 2*sqrt(2) 
    edge_length = cylinder2_width
    box_final_width = (edge_length + cylinder2_width/5 if joint_structure == "clevis" else edge_length)
    box_solid = Workplane("XY").box(edge_length, edge_length, box_final_width)
    # (0,0), (edge_length, edge_length), (edge_length,0) を結んだ三角柱
    triangle_pole = Workplane("XY").polyline([
        (0, 0),
        (edge_length, edge_length),
        (edge_length, 0),
        (0, 0)
    ]).close().extrude(box_final_width/2, both=True)
    triangle_pole = triangle_pole.translate((-edge_length/2, -edge_length/2, 0))
    box_solid = box_solid.cut(triangle_pole).rotate((0, 0, 0), (0, 1, 0), 90).rotate((0, 0, 0), (0, 0, 1), 180).translate((0, cylinder1_length+edge_length/2, 0))

    # cylinder2を作成
    if joint_structure == "clevis":
        cylinder_left = (Workplane("XY").center(0, 0).circle(cylinder2_radius/2.0).extrude(cylinder2_width/10)).rotate((0,0,0),(0,1,0),-90).translate((-cylinder2_width/2.0, cylinder2_offset_y, cylinder2_offset_z))
        cylinder_right = (Workplane("XY").center(0, 0).circle(cylinder2_radius/2.0).extrude(cylinder2_width/10)).rotate((0,0,0),(0,1,0),+90).translate((cylinder2_width/2.0, cylinder2_offset_y, cylinder2_offset_z))

        cylinder = cylinder_left + cylinder_right
    elif joint_structure == "tang":
        cylinder = (Workplane("XY").center(0, 0).circle(cylinder2_radius/2.0).extrude(cylinder2_width/2,both=True)).rotate((0,0,0),(0,1,0),-90).translate((0, cylinder2_offset_y, cylinder2_offset_z))

    else:
        raise ValueError("joint_structure must be 'clevis' or 'tang' or False. If you want to disable the joint structure, set it to False.")

    link_geometry =  box_solid + cylinder + offset_cylinder

    joint_xyz = np.array([0, cylinder2_offset_y, cylinder2_offset_z])
    joint_rpy = np.array([0, 0, 0])

    if reverse:
        link_geometry = link_geometry.translate((0, -cylinder2_offset_y, -cylinder2_offset_z)).rotate((0, 0, 0), (1, 0, 0), 180)


    return Link(
        link_name=link_name,
        link_geometry=link_geometry,
        joint_xyz=joint_xyz,
        joint_rpy=joint_rpy,
        geometry_xyz=np.zeros(3),
        geometry_rpy=np.zeros(3),
    )

def gen_gimbal_link(
    link_name: str,
    torus_radius: float,
    torus_section_radius: float,
    offset_length: float,
    cylinder_radius: float,
    cylinder_height: float,
    cylinder_offset_y: float = 0.0,
    cylinder_offset_z: float = 0.0,
    joint_structure: str  = "clevis",
    reverse:bool = False
) -> Link:
    """
    1/4トーラスと円筒の組み合わせでリンクを生成する。
    円筒の配置はy方向・z方向のオフセットで指定。
    clevis: 横から挟む。tang: 真ん中に配置。
    1/4トーラスから円筒を引き、そのあとunionで足す。

    Args:
        link_name (str): リンク名
        torus_radius (float): トーラスの中心半径
        torus_section_radius (float): トーラス断面半径
        cylinder_radius (float): 円筒半径
        cylinder_height (float): 円筒高さ
        cylinder_offset_y (float): 円筒のY方向オフセット
        cylinder_offset_z (float): 円筒のZ方向オフセット
        root_joint_structure (str|bool): "clevis" or "tang" or False
        tip_joint_structure (str|bool): 未使用
        body_shape (str): 未使用

    Returns:
        Link: 生成したリンク
    """
    # 1/4トーラス作成
    elbow_torus = torus(torus_radius, torus_section_radius)
    filter_box = box(torus_radius, torus_radius, torus_radius).translate((torus_radius/2, torus_radius/2, -torus_radius/2))
    elbow = elbow_torus * filter_box
    elbow = elbow.rotate((0, 0, 0), (0, 1, 0), 90).translate((0, offset_length, torus_radius/2))

    # オフセット長さが設定されている場合、それ分の円筒を作成
    if offset_length > 0:
        offset_cylinder = (
            Workplane("XY")
            .center(0, 0)
            .circle(torus_section_radius/2.0)
            .extrude(offset_length)
        )
        offset_cylinder = offset_cylinder.rotate((0,0,0),(1,0,0),-90)
    else:
        offset_cylinder = cq.Compound.makeCompound([])
    
    # 円筒作成
    if joint_structure == "clevis":
        cylinder_left = (Workplane("XY").center(0, 0).circle(cylinder_radius/2.0).extrude(cylinder_height/10.0)).rotate((0,0,0),(0,1,0),-90).translate((-cylinder_height/2.0, cylinder_offset_y, cylinder_offset_z))
        cylinder_right = (Workplane("XY").center(0, 0).circle(cylinder_radius/2.0).extrude(cylinder_height/10.0)).rotate((0,0,0),(0,1,0),+90).translate((cylinder_height/2.0, cylinder_offset_y, cylinder_offset_z))

        cylinder = cylinder_left + cylinder_right
    elif joint_structure == "tang":
        cylinder = (Workplane("XY").center(0, 0).circle(cylinder_radius/2.0).extrude(cylinder_height)).rotate((0,0,0),(0,1,0),-90).translate((0, cylinder_offset_y, cylinder_offset_z))

    else:
        raise ValueError("joint_structure must be 'clevis' or 'tang' or False. If you want to disable the joint structure, set it to False.")


    # 1/4トーラスから円筒を引く
    # torus_cut = elbow.cut(cylinder)
    torus_cut = elbow

    # 必要なら円筒を足す
    link_geometry = offset_cylinder + torus_cut + cylinder

    # ジョイント位置（トーラスの端点を基準にする例）
    joint_xyz = np.array([torus_radius, torus_radius, 0])
    joint_rpy = np.zeros(3)

    return Link(
        link_name=link_name,
        link_geometry=link_geometry,
        joint_xyz=joint_xyz,
        joint_rpy=joint_rpy,
        geometry_xyz=np.zeros(3),
        geometry_rpy=np.zeros(3),
    )

def gen_wrist_link(
    link_name: str,
    box1_width: float,
    box1_length: float,
    box1_height: float,
    box2_width: float,
    box2_length: float,
    box2_height: float,
    box2_span:float = 0.5,
    box2_offset_y: float = 0.0,
    box2_offset_z: float = 0.0,
    joint_xyz: np.ndarray = None) -> Link:

    # Generate a box1 
    box1 = Workplane("XY").box(box1_width, box1_length, box1_height).translate((0, box1_length/2.0, 0))

    # Generate box2s
    box21 = Workplane("XY").box(box2_width, box2_length, box2_height).translate((box2_span/2, box2_offset_y + box2_length/2, box2_offset_z))
    box22 = Workplane("XY").box(box2_width, box2_length, box2_height).translate((-box2_span/2, box2_offset_y + box2_length/2, box2_offset_z))

    # Combine the boxes
    link_geometry = box1 + box21 + box22

    # set next joint position
    if joint_xyz is None:
        joint_xyz = np.array([0, box1_length + box2_length/2, box2_offset_z])
    joint_rpy = np.zeros(3)

    return Link(link_name=link_name, link_geometry=link_geometry, joint_xyz=joint_xyz, joint_rpy=joint_rpy, geometry_xyz=np.zeros(3), geometry_rpy=np.zeros(3))

def gen_horizontal_link(
    link_name: str,
    link_length: float,
    link_width: float,
    link_height: float,
    root_joint_structure: str | bool = "clevis",
    tip_joint_structure: str | bool = "tang",
    body_shape: str = "box"  # "box"（デフォルト）または "cylinder" を指定
) -> Link:
    """
    Generate a horizontal link with optional joint structures at the root and tip.

    Args:
        link_name (str): Name of the link.
        link_length (float): Length of the link.
        link_width (float): Width of the link (boxの場合は幅、cylinderの場合は直径).
        link_height (float): Height of the link (boxの場合は高さ、cylinderの場合は高さ).
        root_joint_structure (str | bool, optional): Type of joint structure at the root ('clevis', 'tang', True, or False). Defaults to "clevis".
        tip_joint_structure (str | bool, optional): Type of joint structure at the tip ('clevis', 'tang', True, or False). Defaults to "tang".
        body_shape (str, optional): "box"（直方体）または "cylinder"（円筒）. Defaults to "box".

    Returns:
        Link: The generated link object.
    """

    origin = np.zeros(3)
    link_body_length = link_length
    if root_joint_structure:
        link_body_length = link_body_length - link_width/2.0
        if (isinstance(root_joint_structure, str) and root_joint_structure.lower() == "clevis") or root_joint_structure is True:
            root_joint_solid_top = make_d_shape(link_width, link_height/10).translate((0, 0, link_height/2.0 - link_height/10/2.0))
            root_joint_solid_bottom = make_d_shape(link_width, link_height/10).translate((0, 0, -link_height/2.0 + link_height/10/2.0))
            root_joint_solid = root_joint_solid_top.union(root_joint_solid_bottom).rotate((0, 0, 0), (0, 0, 1), 180)
        elif isinstance(root_joint_structure, str) and root_joint_structure.lower() == "tang":
            root_joint_solid = make_d_shape(link_width, 0.75 * link_height).rotate((0, 0, 0), (0, 0, 1), 180)
        else:
            raise ValueError("root_joint_structure must be 'clevis', 'tang' or True. If you want to disable the root joint structure, set it to False.")
        root_joint_solid = root_joint_solid.translate((0, +link_width/2.0, 0))
    else:
        root_joint_solid = cq.Compound.makeCompound([])

    if tip_joint_structure:
        link_body_length = link_body_length - link_width/2.0
        if (isinstance(tip_joint_structure, str) and tip_joint_structure.lower() == "clevis") or tip_joint_structure is True:
            tip_joint_solid_top = make_d_shape(link_width, link_height/10).translate((0, 0, link_height/2.0 - link_height/10/2.0))
            tip_joint_solid_bottom = make_d_shape(link_width, link_height/10).translate((0, 0, -link_height/2.0 + link_height/10/2.0))
            tip_joint_solid = tip_joint_solid_top.union(tip_joint_solid_bottom)
        elif isinstance(tip_joint_structure, str) and tip_joint_structure.lower() == "tang":
            tip_joint_solid = make_d_shape(link_width, 0.75 * link_height)
        else:
            raise ValueError("tip_joint_structure must be 'clevis', 'tang' or True. If you want to disable the root joint structure, set it to False.")
        tip_joint_solid = tip_joint_solid.translate((0, link_length-link_width/2.0, 0))
    else:
        tip_joint_solid = cq.Compound.makeCompound([])

    origin = np.array([0, link_width/2.0 * (1.0 if root_joint_structure else 0.0), 0]) \
            + np.zeros(3) \
            + np.array([0, (link_length - link_width/2.0 * (1.0 if root_joint_structure else 0.0) - link_width/2.0 * (1.0 if tip_joint_structure else 0.0))/2.0, 0])

    # ボディ形状の選択
    if link_body_length > 0:
        if body_shape == "box":
            box_solid = Workplane("XY").box(link_width, link_body_length, link_height).translate(tuple(origin))
        elif body_shape == "cylinder":
            # 円筒の直径=link_width, 高さ=link_body_length, 中心をoriginに合わせる
            # 円筒の長手方向をY軸に合わせる
            box_solid = Workplane("XY").circle(link_width/2).extrude(link_body_length).rotate((0,0,0), (1,0,0), -90).translate(tuple(np.array([0,link_width/2.0* (1.0 if root_joint_structure else 0.0),0])))

        else:
            raise ValueError("body_shape must be 'box' or 'cylinder'")
    else:
        box_solid = cq.Compound.makeCompound([])

    link_geometry = box_solid + root_joint_solid + tip_joint_solid
    joint_xyz = np.array([0, link_length, 0])
    joint_rpy = np.array([0, 0, 0])

    return Link(link_name=link_name, link_geometry=link_geometry, joint_xyz=joint_xyz, joint_rpy=joint_rpy, geometry_xyz=np.zeros(3), geometry_rpy=np.zeros(3))

def gen_simple_cylinder_link(
    link_name: str,
    link_length: float,
    link_radius: float,
    origin_xyz: np.ndarray = np.zeros(3),
    joint_xyz: np.ndarray = None,
    joint_rpy: np.ndarray = None
    ) -> Link:

    # Generate a simple cylinder link
    cylinder = Workplane("XY").circle(link_radius).extrude(link_length)

    cylinder = cylinder.translate(tuple(-origin_xyz))

    if joint_xyz is None:
        joint_xyz = np.array([0, 0, link_length-origin_xyz[2]])
    if joint_rpy is None:
        joint_rpy = np.zeros(3)

    link_geometry = cylinder
    return Link(link_name=link_name, link_geometry=link_geometry, joint_xyz=joint_xyz, joint_rpy=joint_rpy, geometry_xyz=np.zeros(3), geometry_rpy=np.zeros(3))
    

def xyz_axes(vector_xyz: np.ndarray = np.zeros(3),vector_rpy: np.ndarray = np.zeros(3)):
    """X, Y, Z軸を表示する関数"""
    # 赤: X軸、緑: Y軸、青: Z軸
    axis_length = 5  # 円柱の長さ
    axis_radius = 0.2  # 円柱の半径
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
    # mcp.run(transport='stdio')