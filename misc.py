#!/usr/bin/env python3

from numpy import arange, array, size
from sys import float_info
from phidl import Device, Path
import phidl.geometry as pg
import phidl.path as pp
from math import pi, sin

EPS = float_info.epsilon

def _anl_logo_base():
    P = Path()
    P.append(pp.straight(10, 2))
    P.end_angle += 60
    P.append(pp.straight(10, 2))
    P.end_angle += 120
    P.append(pp.straight(30, 2))
    P.end_angle += 120
    P.append(pp.straight(10, 2))
    P.end_angle += 60
    P.append(pp.straight(10, 2))
    P.movex(10)
    return P

def anl_logo(layer = 1, scale = 1):
    out = Device()
    D = Device()
    P1 = _anl_logo_base()
    P2 = _anl_logo_base()
    P3 = _anl_logo_base()
    P2.move(origin = (P2.xmax, P2.ymax), destination = (0, 0))
    P3.move(origin = (P3.xmin, P3.ymax), destination = (20, 0))
    P2.rotate(-120)
    P3.rotate(120, center = (20, 0))
    p1poly = P1.extrude(1, layer = layer)
    p2poly = P2.extrude(1, layer = layer)
    p3poly = P3.extrude(1, layer = layer)
    p1 = D.add_ref(p1poly)
    p2 = D.add_ref(p2poly)
    p3 = D.add_ref(p3poly)
    p2.movex(origin = p2.xmin, destination = p1.xmin)
    p2.movey(origin = p2.ymin, destination = p1.ymin)
    p3.movey(origin = p3.ymin, destination = p1.ymin)
    p3.movex(origin = p3.xmax, destination = p1.xmax)
    L = pg.union(D, layer = layer)
    L.move(origin = L.center, destination = (0, 0))
    logo = out.add_ref(L)
    logo.magnification = scale
    out.flatten()
    out.name = "Logo"
    return out

def alignment_marks(layer = 1):
    D = Device(name = 'Alignment')
    CB = pg.cross(length = 50, width = 5)
    CM = pg.cross(length = 10, width = 1)
    CS = pg.cross(length = 5, width = 0.5)
    bbox = CM.bbox
    small_cross_1 = CM.add_ref(CS)
    small_cross_1.move(origin = small_cross_1.center, destination = (bbox[1, 1], bbox[1, 1]))
    small_cross_2 = CM.add_ref(CS)
    small_cross_2.move(origin = small_cross_2.center, destination = (bbox[1, 1], bbox[0, 1]))
    small_cross_3 = CM.add_ref(CS)
    small_cross_3.move(origin = small_cross_3.center, destination = (bbox[0, 1], bbox[0, 1]))
    small_cross_4 = CM.add_ref(CS)
    small_cross_4.move(origin = small_cross_4.center, destination = (bbox[0, 0], bbox[1, 1]))
    bbox = CB.bbox
    med_cross_1 = CB.add_ref(CM)
    med_cross_1.move(origin = med_cross_1.center, destination = (bbox[1, 1], bbox[1, 1]))
    med_cross_2 = CB.add_ref(CM)
    med_cross_2.move(origin = med_cross_2.center, destination = (bbox[1, 1], bbox[0, 1]))
    med_cross_3 = CB.add_ref(CM)
    med_cross_3.move(origin = med_cross_3.center, destination = (bbox[0, 1], bbox[0, 1]))
    med_cross_4 = CB.add_ref(CM)
    med_cross_4.move(origin = med_cross_4.center, destination = (bbox[0, 0], bbox[1, 1]))
    D.add_ref(CB)
    D = pg.union(D, layer = layer)
    D.name = "AlignmentMarks"
    return D

def bus(n = 3, width = 10, pitch = 20, length = 100, negative = True, trench = 2, layer = 2):
    D = Device()
    R = pg.straight(size = (width, length), layer = layer)
    for i in range(n):
        rect = D.add_ref(R)
        rect.movex(i*pitch)
        D.add_port(name = f'in_{i}', port = rect.ports[2])
        D.add_port(name = f'out_{i}', port = rect.ports[1])
    if negative:
        D = pg.outline(D, distance = trench, open_ports = width+EPS, layer = layer)
    return D

def hall_cross(width = 2, length = 10, connector_width=1, connector_length=2, trench = None, layer = None):
    D = Device()
    IC = pg.compass(size = (connector_width, width), layer = layer)
    C = pg.straight(size = (width, length), layer = layer)
    P = pg.straight(size = (connector_width, connector_length), layer = layer)

    channel_connector1 = D.add_ref(IC)
    channel_connector2 = D.add_ref(IC)
    channel = D.add_ref(C)
    channel.connect(1, channel_connector1.ports['E'])
    channel_connector2.connect("W", channel.ports[2])

    stub1 = D.add_ref(IC)
    stub2 = D.add_ref(IC)
    stub1.connect("E", channel_connector1.ports['W'])
    stub2.connect("W", channel_connector2.ports['E'])

    probe_NW = D.add_ref(P)
    probe_NW.connect(1, channel_connector1.ports['N'])
    probe_SW = D.add_ref(P)
    probe_SW.connect(1, channel_connector1.ports['S'])
    probe_NE = D.add_ref(P)
    probe_NE.connect(1, channel_connector2.ports['N'])
    probe_SE = D.add_ref(P)
    probe_SE.connect(1, channel_connector2.ports['S'])

    D.add_port(name = "channel_in", port=stub1.ports['W'])
    D.add_port(name = "channel_out", port=stub2.ports['E'])
    D.add_port(name = "probe_NW", port=probe_NW.ports[2])
    D.add_port(name = "probe_SW", port=probe_SW.ports[2])
    D.add_port(name = "probe_NE", port=probe_NE.ports[2])
    D.add_port(name = "probe_SE", port=probe_SE.ports[2])
    if trench:
        D = pg.outline(D, distance = trench, open_ports = width+EPS, layer=layer)
    return D

def stiches(device, which_layer, WF=100, WA=None, width=None, layer=0):
    if width is None:
        width = WF/20
    O = Device()
    rh = pg.rectangle((device.xsize, width))
    rv = pg.rectangle((width, device.ysize))
    if WA:
        warr = WA
    else:
        warr = device

    for i in arange(warr.xmin + WF, warr.xmax, WF):
        s = O << rv
        s.movex(i - width/2)
        s.movey(origin=s.y, destination=warr.y)
    for i in arange(warr.ymin + WF, warr.ymax, WF):
        s = O << rh
        s.movey(i - width/2)
        s.movex(origin=s.x, destination=warr.x)

    to_stitch = pg.extract(device, layers=which_layer)
    S = pg.boolean(to_stitch, O, "and", layer=layer)
    S.name = "stitching"
    return S

# Makes an hexagonal array of holes around an object
#   around --> Device that the array is made around
#   a --> lattice parameter
#   size --> the size (x, y) of the array
#   radius --> Radius of each grid point
#   offset --> distance between object and nearest dot
#   layer --> Layer in which end result should  be
#
# Version 1.0: Makes array and subtracts the device plus outline from it
def hole_array(around = None, a = 10, size = (500, 500), radius = 1, offset = 10, layer = 1):
    circle = pg.circle(radius = radius, layer = layer)
    R = Device('Ref')
    disDown = sin(pi/3) * a
    disSide = a/2
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
def hex_Array(avoid = None, box = None, a = 10, radius = 1, offset = 10, layer = 1):
    #Creating end product device and the dots used
    F = Device('Filler')
    cir = pg.circle(radius, layer = layer)
    
    #Calculating the distance between rows and a box around each dot
    disY = sin(pi/3) * a
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
                                      box + array([[a/2, disY], [0, 0]]),
                                      dX, dY)
    
    #Sets of dots
    dots1 = []
    dots2 = []
    
    
    R = Device('Hole Array')
    #Creating each hole
    for row in range(size(allowed1, 0)):
        if row % about == 0:
            dots1.append([])
            for col in range(size(allowed1, 1)):
                if col % about == 0:
                    dots1[int(row/about)].append([])
                    if not allowed1[row][col]:
                        dots1[int(row/about)][int(col/about)] = R.add_ref(cir)
                        dots1[int(row/about)][int(col/about)].move(
                            destination = (dX/2 + int(col/about)*a, dY/2 + int(row/about)*2*disY))
        
        
    for row in range(size(allowed2, 0)):
        if row % about == 0:
            dots2.append([])
            for col in range(size(allowed2, 1)):
                if col % about == 0:
                    dots2[int(row/about)].append([])
                    if not allowed2[row][col]:
                        dots2[int(row/about)][int(col/about)] = R.add_ref(cir)
                        dots2[int(row/about)][int(col/about)].move(
                            destination = (dX/2 + a/2 + int(col/about)*a, dY/2 + disY + int(row/about)*2*disY))

    return R