import cadquery as cq
import numpy as np
from cadquery.vis import show
from cadquery import Workplane
import math
# 頂点ファイルのパス
file_path = "../Torus/torus_parameter.txt"  # ここを書き換えてください

# ファイルから x, z の頂点を読み込む
points = []
with open(file_path, 'r') as f:
    for line in f:
        print(line)
        line = line.strip()
        if line.startswith("#") or line == "":
            continue
        x_str, z_str = line.split()
        x = float(x_str)
        z = float(z_str)
        points.append(cq.Vector(x, 0, z))




# スプライン補間されたワイヤ（閉じたループ）
spline_wire = cq.Workplane("XZ").spline(points).close()

# z軸周りに360度回転してトーラス形状を作成
torus_solid = spline_wire.revolve(angleDegrees=360, axisStart=(0, 0, 0), axisEnd=(0, 0, 1))

# 表示（JupyterやCQ-editor使用時）
# show(torus_solid.rotate((1, 0, 0), (0, 0, 0), -90))

torus_rotated = torus_solid.rotate((1, 0, 0), (0, 0, 0), -90)

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

asm = cq.Assembly()
asm.add(torus_rotated, name="Torus", color=cq.Color(0.8, 0.8, 0.8))
asm.add(xyz_axes(), name="XYZ_Axes")

# 表示
show(asm)