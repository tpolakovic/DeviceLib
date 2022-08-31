#!/usr/bin/env python3

from phidl import Device, Path
import phidl.geometry as pg
import phidl.path as pp

def _anl_logo_base():
    D = Device()
    P = Path()
    P.append(pp.straight(10,2))
    P.end_angle += 60
    P.append(pp.straight(10,2))
    P.end_angle +=120
    P.append(pp.straight(30,2))
    P.end_angle +=120
    P.append(pp.straight(10,2))
    P.end_angle +=60
    P.append(pp.straight(10,2))
    P.movex(10)
    return P

def anl_logo(layer=1, scale=1):
    D = Device()
    P1 = _anl_logo_base()
    P2 = _anl_logo_base()
    P3 = _anl_logo_base()
    P2.move(origin=(P2.xmax, P2.ymax), destination=(0,0))
    P3.move(origin=(P3.xmin, P3.ymax), destination=(20,0))
    P2.rotate(-120)
    P3.rotate(120, center=(20,0))
    p1poly = P1.extrude(1, layer=layer)
    p2poly = P2.extrude(1, layer=layer)
    p3poly = P3.extrude(1, layer=layer)
    p1 = D.add_ref(p1poly)
    p2 = D.add_ref(p2poly)
    p3 = D.add_ref(p3poly)
    p2.movex(origin=p2.xmin, destination=p1.xmin)
    p2.movey(origin=p2.ymin, destination=p1.ymin)
    p3.movey(origin=p3.ymin, destination=p1.ymin)
    p3.movex(origin=p3.xmax, destination=p1.xmax)
    D = pg.union(D, layer=layer)
    D.move(origin=D.center, destination=(0,0))
    D.polygons[0].scale(scale)
    return D

def alignment_marks(layer=1):
    D = Device(name='Alignment')
    CB = pg.cross(length=50, width=5)
    CM = pg.cross(length=10, width=1)
    CS = pg.cross(length=5, width=0.5)
    bbox = CM.bbox
    small_cross_1 = CM.add_ref(CS)
    small_cross_1.move(origin=small_cross_1.center, destination=(bbox[1,1], bbox[1,1]))
    small_cross_2 = CM.add_ref(CS)
    small_cross_2.move(origin=small_cross_2.center, destination=(bbox[1,1], bbox[0,1]))
    small_cross_3 = CM.add_ref(CS)
    small_cross_3.move(origin=small_cross_3.center, destination=(bbox[0,1], bbox[0,1]))
    small_cross_4 = CM.add_ref(CS)
    small_cross_4.move(origin=small_cross_4.center, destination=(bbox[0,0], bbox[1,1]))
    bbox = CB.bbox
    med_cross_1 = CB.add_ref(CM)
    med_cross_1.move(origin=med_cross_1.center, destination=(bbox[1,1], bbox[1,1]))
    med_cross_2 = CB.add_ref(CM)
    med_cross_2.move(origin=med_cross_2.center, destination=(bbox[1,1], bbox[0,1]))
    med_cross_3 = CB.add_ref(CM)
    med_cross_3.move(origin=med_cross_3.center, destination=(bbox[0,1], bbox[0,1]))
    med_cross_4 = CB.add_ref(CM)
    med_cross_4.move(origin=med_cross_4.center, destination=(bbox[0,0], bbox[1,1]))
    big_cross = D.add_ref(CB)
    D = pg.union(D, layer=layer)
    return D
