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


a = gen_gimbal_link2(link_name="GimbalLink",
                      cylinder1_radius=2,
                      cylinder1_length=2.2,
                      cylinder2_offset_y=3,
                      cylinder2_offset_z=1,
                      cylinder2_radius=2,
                      cylinder2_width=1.5)
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
                      joint_structure="tang")
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
                      joint_structure="clevis")
xyz = xyz_axes(np.array([0, 0, 0]), np.array([0, 0, 0]))

# aと xyzを組み合わせて表示
asm = cq.Assembly()
asm.add(a, name="D_shape", color=cq.Color(0.5, 0.5, 0.5))  # グレー
asm.add(xyz, name="Axes")

show(asm)
# a = gen_horizontal_link(link_name="Link1", link_length=10, link_width=5, link_height=5, body_shape="cylinder").link_geometry
# show(a)