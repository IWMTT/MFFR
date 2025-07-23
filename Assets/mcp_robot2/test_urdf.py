from urchin import URDF
robot = URDF.load('test_robot.urdf')
for link in robot.links:
    print(link.name)


robot.show()