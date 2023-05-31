#!/usr/bin/env python

import numpy as np
from phidl import Device, Layer
import phidl.geometry as pg
import phidl.path as pp

def launchpad(size = (350, 350), wire_width = 50, negative = True, trench = 10, layer = None, metal_layer = None,
              shadow_layer = None, shadow_extra = 20):
    size = np.array(size)
    out = Device("Launchpad")
    D = Device()
    P1 = pg.compass(size = size, layer = layer)
    T1 = pg.taper(length = size[0]/3, width1 = size[1], width2 = wire_width, layer = layer)
    ip = D.add_ref(P1)
    it = D.add_ref(T1)
    ip.movex(-size[0]/2)
    it.connect(port=1, destination=ip.ports['E'])
    out.add_port(name = 1, port = it.ports[2])

    GP = pg.rectangle(size = size*0.9, layer = metal_layer)
    gp = out.add_ref(GP)
    gp.move(origin=gp.center, destination=ip.center)

    D2 = Device()
    P2 = pg.compass(size = (size[0] * 1.5, size[1] * 2), layer = layer)
    T2 = pg.taper(length = size[0]/3, width1 = P2.ysize, width2 = wire_width + 2 * trench, layer = layer)
    op = D2.add_ref(P2)
    ot = D2.add_ref(T2)
    op.movex(origin=op.xmax, destination=0)
    ot.connect(port=1, destination=op.ports['E'])

    Dout = pg.boolean(D, D2, 'B-A', layer = layer)

    out << Dout
    return out

def pad(size = (350, 350), wire_width = 50, negative = True, trench = 10, layer = None, metal_layer = None,
                shadow_layer = None, shadow_extra = 20):
    if not negative:
        trench = 0
    size = np.array(size)
    D = Device()
    if trench < wire_width:
        T = pg.tee(size = size, stub_size = (wire_width, wire_width), taper_type = 'fillet', layer = layer)
    else:
        T = pg.tee(size = size, stub_size = (wire_width, trench), taper_type = 'fillet', layer = layer)
    D.add_port(name = 1, port = T.ports[3])
    T.remove([T.ports[1], T.ports[2]])
    D.flatten()
    if negative:
        T = pg.outline(T, distance = trench, open_ports = trench+1, layer = layer)
    P = pg.rectangle(size = size*0.9, layer = metal_layer)
    P.move(origin = P.center, destination = (0, size[1]/2))
    D.add_ref(T)
    if negative:
        D.add_ref(P)
    S = pg.rectangle(size = D.size+shadow_extra, layer = shadow_layer)
    S.move(origin = S.center, destination = D.center)
    D.add_ref(S)
    D.flatten()
    D.move(origin=D.center, destination=(0,0))
    D.name = "Pad"
    return D

def fan(size = (100, 50), wire_width = 50, trench = 10, layer = None, optimize=None):
    layer1 = Layer(layer, 1000)
    D = Device()
    P = pp.euler(radius = size[1], use_eff = True)
    P.append(pp.straight(length = size[0]-size[1]))
    segment = P.extrude(trench, layer = layer1)
    top = D.add_ref(segment)
    bottom = D.add_ref(segment)
    top.movey(0.5*wire_width+0.5*trench)
    bottom.mirror((0, 0), (1, 0))
    bottom.movey(-0.5*wire_width-0.5*trench)
    D.add_port(name = 'out', midpoint = [size[1]/2, 0], width = size[0]+wire_width, orientation = 0)
    D.add_port(name = '_in', midpoint = [0, 0], width = wire_width, orientation = 180)
    if optimize:
        ST = pg.optimal_step(start_width=optimize, end_width=wire_width, symmetric=True)
        ST = pg.outline(ST, distance=trench, open_ports=2*trench, layer=layer)
        step = D << ST
        step.connect(2, D.ports['_in'])
        D.add_port(name = 'in', port=step.ports[1])
        D.remove(D.ports['_in'])
    else:
        D.add_port(name = 'in', port=D.ports['_in'])
        D.remove(D.ports['_in'])
    D.flatten()
    D.name = "Fan"
    return D
