import os
import math
distance1=10.26
distance0=[-0.005,0,-0.005,0,0.005,-0.005,-0.005,0,-0.005,-0.01,-0.008,-0.005,-0.01,-0.02,-0.015,-0.02]
#distance0=[0.005,0.012,0.014,0,0.002,0,0,0,0,0,0.007,0,0,0,0.017,0,0.006,0,0.01,0.013,0.016,0.02,0.016,0.017,0,0.015]
angles=[]
for id,distance in enumerate(distance0):
    radis=math.atan(distance/distance1)
    angle=180*radis/math.pi
    angle=round(angle,3)
    #angles.append(angle)
    if angle < 170:
        angles.append(angle)
    else:
        angle=180-angle
        angles.append(-angle)

error=30*math.tan(angle)
print(angles)
print(len(distance0))


# print(10*math.tan(math.pi*0.1/180))
x=10.26*math.tan(0.02/180*math.pi)
print(x)