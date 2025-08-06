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
link_01 = gen_horizontal_link(
    link_name="link_01",
    link_length=1.0,
    link_width=0.7,
    link_height=0.375*2,
    root_joint_structure=False,
    tip_joint_structure="Clevis",
    body_shape="box"
).link_geometry

xyz = xyz_axes(np.array([0, 0, 0]), np.array([0, 0, 0]))

asm = cq.Assembly()
asm.add(link_01, name="link_01", color=cq.Color(0.5, 0.5, 0.5))
asm.add(xyz, name="Axes")

show(asm)

link_07 = gen_horizontal_link(
    link_name="link_07",
    link_length=0.62,
    link_width=0.48,
    link_height=0.44,
    root_joint_structure=False,
    tip_joint_structure="tang",
    body_shape="box"
).link_geometry

xyz = xyz_axes(np.array([0, 0, 0]), np.array([0, 0, 0]))

asm = cq.Assembly()
asm.add(link_07, name="link_07", color=cq.Color(0.5, 0.5, 0.5))
asm.add(xyz, name="Axes")

show(asm)


# gen_horizontal_linkを使ってhorizontal_linkを生成
horizontal_link = gen_horizontal_link(
    link_name="HorizontalLink",
    link_length=10,
    link_width=5,
    link_height=5,
    body_shape="box"
).link_geometry

xyz = xyz_axes(np.array([0, 0, 0]), np.array([0, 0, 0]))

link_08 = gen_wrist_link(
    link_name="link_08",
    box1_width=0.8,
    box1_length=0.32,
    box1_height=0.52,
    box2_width=0.2,
    box2_length=1.0,
    box2_height=0.2,
    box2_span=0.72,
    box2_offset_y=0.0,
    box2_offset_z=0.2,
    joint_xyz=np.array([0.0, 0.68, 0.2])
).link_geometry

asm = cq.Assembly()
asm.add(link_08, name="link_08", color=cq.Color(0.5, 0.5, 0.5))
asm.add(xyz, name="Axes")
show(asm)

# horizontal_linkとxyzを組み合わせて表示
asm = cq.Assembly()
asm.add(horizontal_link, name="HorizontalLink", color=cq.Color(0.5, 0.5, 0.5))
asm.add(xyz, name="Axes")

show(asm)

# gen_horizontal_linkを使ってhorizontal_linkを生成
horizontal_link = gen_horizontal_link(
    link_name="HorizontalLink",
    link_length=10,
    link_width=5,
    link_height=5,
    body_shape="box",
    tip_joint_structure="clevis",
    root_joint_structure="tang"
).link_geometry

xyz = xyz_axes(np.array([0, 0, 0]), np.array([0, 0, 0]))

# horizontal_linkとxyzを組み合わせて表示
asm = cq.Assembly()
asm.add(horizontal_link, name="HorizontalLink", color=cq.Color(0.5, 0.5, 0.5))
asm.add(xyz, name="Axes")

show(asm)



a = gen_gimbal_link2(link_name="GimbalLink",
                      cylinder1_radius=2,
                      cylinder1_length=2.2,
                      cylinder2_offset_y=3,
                      cylinder2_offset_z=1,
                      cylinder2_radius=2,
                      cylinder2_width=1.5).link_geometry
xyz = xyz_axes(np.array([0, 0, 0]), np.array([0, 0, 0]))

# aと xyzを組み合わせて表示
asm = cq.Assembly()
asm.add(a, name="D_shape", color=cq.Color(0.5, 0.5, 0.5))  # グレー
asm.add(xyz, name="Axes")

show(asm)

a = gen_gimbal_link2(link_name="GimbalLink",
                      cylinder1_radius=2,
                      cylinder1_length=2.2,
                      cylinder2_offset_y=3,
                      cylinder2_offset_z=1,
                      cylinder2_radius=2,
                      cylinder2_width=1.5,
                      joint_structure="tang").link_geometry
xyz = xyz_axes(np.array([0, 0, 0]), np.array([0, 0, 0]))

# aと xyzを組み合わせて表示
asm = cq.Assembly()
asm.add(a, name="D_shape", color=cq.Color(0.5, 0.5, 0.5))  # グレー
asm.add(xyz, name="Axes")

show(asm)

a = gen_gimbal_link2(link_name="GimbalLink",
                      cylinder1_radius=2,
                      cylinder1_length=2.2,
                      cylinder2_offset_y=3,
                      cylinder2_offset_z=1,
                      cylinder2_radius=2,
                      cylinder2_width=1.5,
                      joint_structure="clevis",reverse=True).link_geometry
xyz = xyz_axes(np.array([0, 0, 0]), np.array([0, 0, 0]))

# aと xyzを組み合わせて表示
asm = cq.Assembly()
asm.add(a, name="D_shape", color=cq.Color(0.5, 0.5, 0.5))  # グレー
asm.add(xyz, name="Axes")

show(asm)
# a = gen_horizontal_link(link_name="Link1", link_length=10, link_width=5, link_height=5, body_shape="cylinder").link_geometry
# show(a)


a = gen_base_rail_link(
    link_name="BaseRailLink",
    rail_length=10.0,
    rail_width=2.0,
    rail_size=0.1,
    origin_xyz=np.zeros(3),
    origin_rpy=np.zeros(3),
    joint_xyz=None,
    joint_rpy=None
).link_geometry
xyz = xyz_axes(np.array([0, 0, 0]), np.array([0, 0, 0]))

# aと xyzを組み合わせて表示
asm = cq.Assembly()
asm.add(a, name="D_shape", color=cq.Color(0.5, 0.5, 0.5))  # グレー
asm.add(xyz, name="Axes")

show(asm)


aa = gen_simple_cylinder_link(
    link_name= "SympleCylinderLink",
    link_length= 5.0,
    link_radius= 1.0,
    origin_xyz= np.array([0, 0, 1]),
    joint_xyz= None,
    joint_rpy= None
    )
a = aa.link_geometry

xyz = xyz_axes(np.array([0, 0, 0]), np.array([0, 0, 0]))

xyz2 =  xyz_axes(gen_simple_cylinder_link(
    link_name= "SympleCylinderLink",
    link_length= 5.0,
    link_radius= 1.0,
    origin_xyz= np.array([0, 0, 1]),
    joint_xyz= None,
    joint_rpy= None
    ).joint_xyz, np.zeros(3))

# aと xyzを組み合わせて表示
asm = cq.Assembly()
asm.add(a, name="D_shape", color=cq.Color(0.5, 0.5, 0.5))  # グレー
asm.add(xyz, name="Axes")
asm.add(xyz2, name="JointAxes", color=cq.Color(1.0, 0.0, 0.0))  # 赤色の軸

show(asm)