# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 10:46:00 2024

@author: Sbaspn

Array of Hexagonal Holes Around an Arbitrary Object
Version 2.1
"""

from phidl import Device
import phidl.geometry as pg
import numpy as np

# Makes an hexagonal array of holes around an object
#   around --> Device that the array is made around
#   a --> lattice parameter
#   size --> the size (x, y) of the array
#   radius --> Radius of each grid point
#   offset --> distance between object and nearest dot
#   layer --> Layer in which end result should  be
#
# Version 1.0
def hole_array(around = None, a = 10, size = (500, 500), radius = 1, offset = 10, layer = 1):
    circle = pg.circle(radius = radius, layer = layer)
    R = Device('Ref')
    disDown = np.sin(np.pi/3) * a
    disSide = np.cos(np.pi/3) * a
    dots = []
    dots2 = []
    for up in range(int(size[1]/2/a)):
        dots.append([])
        for i in range(int(size[0]/a)):
            dots[up].append(R.add_ref(circle))
            dots[up][i].move(destination = (i*a, up*2*a))
    for up2 in range(int((size[1]-disDown)/2/a)):
        dots2.append([])
        for i2 in range(int((size[0]-disSide)/a)):
            dots2[up2].append(R.add_ref(circle))
            dots2[up2][i2].move(destination = (disSide + i2*a, a + up2*2*a))
    R = R.move(destination = (-size[0]/2, -size[1]/2))
    
    L = Device('L')
    if around is None:
        L.add_ref(R)
        return L
    O = Device('overall')
    dt = O.add_ref(R)
    ar1 = O.add_ref(around)
    ar2 = pg.outline(around, distance=offset, layer=layer)
    
    sub2 = pg.boolean(dt, ar2, 'not', layer = layer)
    sub1 = pg.boolean(sub2, ar1, 'not', layer = layer)
    
    fin = L.add_ref(sub1)
    fin2 = L.add_ref(around)
    return L

# Makes an hexagonal array of holes around an object
#   avoid --> Device that the array is made around
#   box --> Box in which the array is contained [x1, y1]
#                                               [x2, y2]
#   a --> lattice parameter
#   radius --> Radius of each grid point
#   offset --> distance between object and nearest dot
#   layer --> Layer in which end result should  be
#
# Version 2.1
#   Issues: When the circles are big enough, they are outside the raster,
#               thus meaning they can be out of bounds
#           When the circles are small enough, the raster boxes can be too big,
#               which then fails to make boxes near the object
def hex_Array(avoid = None, box = None, a = 10, radius = 1, offset = 10, layer = 1):
    #Creating end product device and the dots used
    F = Device('Filler')
    cir = pg.circle(radius, layer = layer)
    
    #Calculating the distance between rows and a box around each dot
    disY = np.sin(np.pi/3) * a
    about = 2*radius
    
    #If the box is not defined, it becomes the boundary box for input device
    if box is None:
        box = avoid.bbox
        
    #Creating a temporary device for creating a raster array on
    tempDev = Device('offset device')
    purse = tempDev.add_ref(avoid)
    liner = pg.outline(avoid, offset)
    bag = tempDev.add_ref(liner)
    
    #Converting the objects into a list of polygons
    shapes = tempDev.get_polygons()
    
    #Raster array box size
    dX = a/about
    dY = 2*disY/about
    
    #Creating raster arrays, where false means the space is free
    allowed1 = pg._rasterize_polygons(shapes,
                                      box,
                                      dX, dY)
    allowed2 = pg._rasterize_polygons(shapes,
                                      box + np.array([[a/2, disY], [0, 0]]),
                                      dX, dY)
    
    #Sets of dots
    dots1 = []
    dots2 = []
    
    
    tempD2 = Device('EVEN MORE THAN THE LAST')
    #Creating each dot
    for row in range(np.size(allowed1, 0)):
        if row % about == 0:
            dots1.append([])
            for col in range(np.size(allowed1, 1)):
                if col % about == 0:
                    dots1[int(row/about)].append([])
                    if not allowed1[row][col]:
                        dots1[int(row/about)][int(col/about)] = tempD2.add_ref(cir)
                        dots1[int(row/about)][int(col/about)].move(
                            destination = (dX/2 + int(col/about)*a, dY/2 + int(row/about)*2*disY))
        
        
    for row in range(np.size(allowed2, 0)):
        if row % about == 0:
            dots2.append([])
            for col in range(np.size(allowed2, 1)):
                if col % about == 0:
                    dots2[int(row/about)].append([])
                    if not allowed2[row][col]:
                        dots2[int(row/about)][int(col/about)] = tempD2.add_ref(cir)
                        dots2[int(row/about)][int(col/about)].move(
                            destination = (dX/2 + a/2 + int(col/about)*a, dY/2 + disY + int(row/about)*2*disY))
    
    temp2 = F.add_ref(tempD2)
    temp2.move(destination = box[0])
    temp = F.add_ref(avoid)
    return F