#!/usr/bin/env python3

from numpy import arange
from sys import float_info
from phidl import Device, Path
import phidl.geometry as pg
import phidl.path as pp

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
        D = pg.outline(D, distance = trench, open_ports = width+EPS)
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
