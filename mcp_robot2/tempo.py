import cadquery as cq
from cadquery.vis import show

# 形状A
box1 = cq.Workplane("XY").box(10, 10, 2)

# 形状B（少し重なる）
box2 = cq.Workplane("XY").box(8, 8, 2).translate((1, 1, 0))

# 一致部分（共通体積）
common = box1.intersect(box2)

show(box2)