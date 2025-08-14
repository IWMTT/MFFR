import cadquery as cq
import numpy as np
from cadquery.vis import show
from cadquery import Workplane
import math
from link_and_joint_class import *
import os
import shutil

# 頂点ファイルのパス
TORUS_DIRECTORY = "../MFFRUnity/Assets/Torus" # Unityプロジェクトのうち、トーラスのパラメータや頂点情報が格納されているディレクトリ
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

print(average_length_inner)

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

blankets = []
alpha = 0.1  # 曲率補正の強さ（調整パラメータ）
# normalsの数だけ、forを回す
for i in range(len(normals)):
    normal = normals[i]
    origin = origins[i]
    normal_next = normals[(i + 1) % len(normals)]
    normal_prev = normals[(i - 1) % len(normals) if i>0 else 0]
    # 正規化
    normal_vector = normal / np.linalg.norm(normal)
    normal_next_vector = normal_next / np.linalg.norm(normal_next)
    normal_prev_vector = normal_prev / np.linalg.norm(normal_prev)

    # --- 曲率計算 ---
    # 進行方向の角度
    ang1 = math.atan2(normal_prev_vector[1], normal_prev_vector[0])
    ang2 = math.atan2(normal_next_vector[1], normal_next_vector[0])
    # 角度差を -pi～pi に正規化
    delta_angle = (ang2 - ang1 + math.pi) % (2 * math.pi) - math.pi

    print(delta_angle)

    # 前後originの距離（弧長近似）
    arc_length = np.linalg.norm(origins[(i + 1) % len(normals)] - origins[(i - 1) % len(normals)])
    curvature = abs(delta_angle) / arc_length if arc_length > 1e-6 else 0.0

    # --- offset計算（曲率補正）---
    base_offset = (average_length_inner) / 2 - 0.025
    offset = base_offset / (1 + alpha * curvature)

    # normal_vectorが[x, y]なら、垂直方向は[-y, x]または[y, -x]
    perp_vector = np.array([-normal_vector[1], normal_vector[0]])
    perp_vector = perp_vector / np.linalg.norm(perp_vector)  # 念のため正規化
    perp_vector2 = np.array([-normal_next_vector[1], normal_next_vector[0]])
    perp_vector2 = perp_vector2 / np.linalg.norm(perp_vector2)  # 念のため正規化
    point1 = origin + perp_vector * offset
    point2 = origin - perp_vector * offset
    # point1, point2から、normal_vector方向に±thickness分だけ伸ばした点を計算
    point_a = point1 + normal_vector * thickness
    point_b = point1 - normal_vector * thickness
    point_c = point2 - normal_vector * thickness
    point_d = point2 + normal_vector * thickness
    # print(f"Normal {i}: {normal}, Origin {i}: {origin}, Points: {point_a}, {point_b}, {point_c}, {point_d}")
    # point_a ~ dを使って、wireframe_cutを生成
    face_intersect =  cq.Face.makeFromWires(cq.Workplane("XZ").polyline([point_a, point_b, point_c, point_d]).close().wire().val())

    # face_origとface_intersectを一緒に表示
    # show([face_orig, face_intersect, xyz_axes()])

    # face_origとface_intersectの交差部分を取得
    face_to_revolve = face_orig * face_intersect

    # rotation_angles をもとに、face_to_revolveを回転させてブランケットを生成
    print(f"Rotation angle for blanket {i}: {rotation_angles[i]} degrees")
    radius = abs(origin[0])  # normal_vector が生えている x座標を半径とみなす

    if radius > 1e-6:
        delta_theta_deg = (0.025 / radius) * (180.0 / math.pi)
    else:
        delta_theta_deg = 0.0  # 半径が小さすぎる場合の保険

    # 回転角を補正：クリアランスのため、両側で合計0.05m相当分角度を減らす
    revolve_angle = rotation_angles[i] - 2 * delta_theta_deg
    half_revolve = revolve_angle / 2.0


    blanket1 = cq.Workplane("XY").add(face_to_revolve).revolve(angleDegrees=half_revolve, axisStart=(0, 0, 0), axisEnd=(0, 0, 1))
    blanket2 = cq.Workplane("XY").add(face_to_revolve).revolve(angleDegrees=half_revolve, axisStart=(0, 0, 0), axisEnd=(0, 0, -1))
    blanket = blanket1.union(blanket2)

    blankets.append(blanket)

# show([blankets, xyz_axes()])

### blanketを1こずつstlに出力する
#### unityプロジェクトのAssets/Torus/Meshが存在していたら削除して再作成する

if os.path.exists(mesh_dir):
    shutil.rmtree(mesh_dir)
os.makedirs(mesh_dir)


for blanket in blankets:
    asm = cq.Assembly()
    asm.add(blanket, name=f"blanket_{blankets.index(blanket)}", color=cq.Color(0.5, 0.5, 0.5))
    asm.export(f"{mesh_dir}/BLKT_{blankets.index(blanket)+1}.gltf", tolerance=5, angularTolerance=1)



# blanketsをstlに出力する前に、1つにまとめる
for i in range(len(blankets)):
    if i == 0:
        combined_blanket = blankets[i]
    else:
        combined_blanket = combined_blanket.union(blankets[i])
# # combined_blanketをstlに出力
cq.exporters.export(combined_blanket, "combined_blanket_51.stl",    tolerance=5, angularTolerance=1 )
cq.exporters.export(combined_blanket, "combined_blanket_lowpoly.stl",    tolerance=5, angularTolerance=1 )
cq.exporters.export(combined_blanket, "combined_blanket_normal.stl",    tolerance=2.5, angularTolerance=0.5 )
cq.exporters.export(combined_blanket, "combined_blanket_fine.stl",    tolerance=1, angularTolerance=0.1 )
