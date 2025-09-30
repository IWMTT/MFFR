import cadquery as cq
import numpy as np
from cadquery.vis import show
from cadquery import Workplane
import math
from link_and_joint_class import *
import os
import shutil

# 頂点ファイルのパス
TORUS_DIRECTORY = "../test" # Unityプロジェクトのうち、トーラスのパラメータや頂点情報が格納されているディレクトリ
# file_path = f"{TORUS_DIRECTORY}/torus_parameter.txt"  #
inner_desc = f"{TORUS_DIRECTORY}/inner_unity.txt" #各ブランケットの、内側頂点情報
outer_desc = f"{TORUS_DIRECTORY}/outer_unity.txt" #各ブランケットの、外側頂点情報
normal_desc = f"{TORUS_DIRECTORY}/normals_unity.txt" #各ブランケットの、法線ベクトル
coordinates_desc = f"{TORUS_DIRECTORY}/blanket_toroidal_coordinates.txt"
mesh_dir = f"{TORUS_DIRECTORY}/Mesh" #メッシュ出力先k

thickness = 1.0

# normal_descから、法線ベクトルのデータを取得する
normals = []
origins = []
with open(normal_desc, 'r') as f:
    for line in f:

        line = line.strip()
        if line.startswith("#") or line == "":
            continue
        x_orig, y_orig, x_normal, y_normal  = line.split(",")
        x_normal = float(x_normal)
        y_normal = float(y_normal)
        x_orig = float(x_orig)
        y_orig = float(y_orig)
        normals.append(np.array([x_normal, y_normal]))
        origins.append(np.array([x_orig, y_orig]))

# inner_descとouter_descの中身の頂点情報を用いて、トーラス断面形状を作成する
# inner_desc + 逆順にしたouter_desc 
points_inner = []
with open(inner_desc, 'r') as f:
    for line in f:

        line = line.strip()
        if line.startswith("#") or line == "":
            continue
        x_str, z_str = line.split(",")
        x = float(x_str)
        z = float(z_str)
        points_inner.append(cq.Vector(x, z, 0))
    # points_innerで構成したpolylineの総長さを、normalsの数で割る
    total_length_inner = sum((points_inner[i] - points_inner[i - 1]).Length for i in range(1, len(points_inner)))
    num_normals = len(normals)  # 法線ベクトルの数
    if num_normals > 0:
        average_length_inner = total_length_inner / num_normals
    else:
        average_length_inner = 0

# print(average_length_inner)

points_outer = []
with open(outer_desc, 'r') as f:
    for line in f:

        line = line.strip()
        if line.startswith("#") or line == "":
            continue
        x_str, z_str = line.split(",")
        x = float(x_str)
        z = float(z_str)
        points_outer.append(cq.Vector(x, z, 0))
points_outer.reverse()

points = points_inner + points_outer

# coordinates_desc を使って、それぞれのブランケットを何度回転押し出しするかを決定する
rotation_angles = []
with open(coordinates_desc, 'r') as f:
    for line in f:
        line = line.strip()
        if line.startswith("#") or line == "":
            continue
        rotation_around_z, extrude_angle_around_z,_ = line.split(",")
        angle = float(extrude_angle_around_z)
        rotation_angles.append(angle)

# ワイヤフレームを生成する（直線で結ぶ）
face_orig =  cq.Face.makeFromWires(cq.Workplane("XZ").spline(points).close().wire().val())


# 上部に四角形を追加して、face_origに足し合わせる
# (6.2,3.9)を中心として、一辺が2mの四角形の4点
point1 = cq.Vector(6.2 - 1.0, 3.9 - 1.0, 0)
point2 = cq.Vector(6.2 + 1.0, 3.9 - 1.0, 0)
point3 = cq.Vector(6.2 + 1.0, 3.9 + 1.0, 0)
point4 = cq.Vector(6.2 - 1.0, 3.9 + 1.0, 0)
face_square = cq.Face.makeFromWires(cq.Workplane("XZ").polyline([point1, point2, point3, point4]).close().wire().val())

# face_origにface_squareを足し合わせる
face_orig = face_orig.fuse(face_square)

# innnerで構成される断面形状を作成
face_inner =  cq.Face.makeFromWires(cq.Workplane("XZ").spline(points_inner).close().wire().val())  

# face_origからface_innerを引いた形状を作成
face_orig = face_orig.cut(face_inner)


blankets = []
alpha = 0.1  # 曲率補正の強さ（調整パラメータ）


# blanket1 = cq.Workplane("XY").add(face_orig).revolve(angleDegrees=7.5/2.0, axisStart=(0, 0, 0), axisEnd=(0, 0, 1))
# blanket2 = cq.Workplane("XY").add(face_orig).revolve(angleDegrees=7.5/2.0, axisStart=(0, 0, 0), axisEnd=(0, 0, -1))
# blanket = blanket1.union(blanket2)

# blankets.append(blanket)


# どの半径で、ブランケットを分割するかを設定する
radius_to_divide = 6.0  # 例: 半径6mで分割

slit = 0.05  # スリットの幅

# inner の生成
# 外側を刈り取るような、大きな四角形を作成
point1 = cq.Vector(radius_to_divide - slit/2.0  , -100.0, 0)
point2 = cq.Vector(radius_to_divide + 100.0     , -100.0, 0)
point3 = cq.Vector(radius_to_divide + 100.9     , +100.0, 0)
point4 = cq.Vector(radius_to_divide - slit/2.0  , +100.0, 0)
face_square = cq.Face.makeFromWires(cq.Workplane("XZ").polyline([point1, point2, point3, point4]).close().wire().val())

face_inner = face_orig.cut(face_square)

blanket1 = cq.Workplane("XY").add(face_inner).revolve(angleDegrees=22.5/2/2.0, axisStart=(0, 0, 0), axisEnd=(0, 0, 1))
blanket2 = cq.Workplane("XY").add(face_inner).revolve(angleDegrees=22.5/2/2.0, axisStart=(0, 0, 0), axisEnd=(0, 0, -1))
blanket = blanket1.union(blanket2)

blankets.append(blanket)
# outer の生成
# 内側を刈り取るような、大きな四角形を作成
point1 = cq.Vector(0.0  , -100.0, 0)
point2 = cq.Vector(radius_to_divide + slit/2.0     , -100.0, 0)
point3 = cq.Vector(radius_to_divide + slit/2.0     , +100.0, 0)
point4 = cq.Vector(0.0  , +100.0, 0)
face_square = cq.Face.makeFromWires(cq.Workplane("XZ").polyline([point1, point2, point3, point4]).close().wire().val())

face_outer = face_orig.cut(face_square)
blanket1 = cq.Workplane("XY").add(face_outer).revolve(angleDegrees=7.5/2.0, axisStart=(0, 0, 0), axisEnd=(0, 0, 1))
blanket2 = cq.Workplane("XY").add(face_outer).revolve(angleDegrees=7.5/2.0, axisStart=(0, 0, 0), axisEnd=(0, 0, -1))
blanket = blanket1.union(blanket2)
blankets.append(blanket)

# Todo 
# 上記をもとに、easyfea向けのdescriptionを作成する。
# Point definition using torus parameters 
# if identical inboard is specified, straighten the inboard edge
# generate discritized points along thee edges
# hollow section 
# rotating extrusion
# ここの具体的なやり方としては、class EasyFEA.fem.Meshのnodes_hogehgoe()系を使う。point かNodes_Domainかなあ

# get fixed nodes
# get loading nodes

if os.path.exists(mesh_dir):
    shutil.rmtree(mesh_dir)
os.makedirs(mesh_dir)


for blanket in blankets:
    asm = cq.Assembly()
    asm.add(blanket, name=f"blanket_{blankets.index(blanket)}", color=cq.Color(0.5, 0.5, 0.5))
    asm.export(f"{mesh_dir}/BLKT_{blankets.index(blanket)+1}.gltf", tolerance=0.1, angularTolerance=0.1)

print(f"Exported {len(blankets)} blankets to {mesh_dir}")

