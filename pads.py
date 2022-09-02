#!/usr/bin/env python3

import numpy as np
from phidl import Device, Layer
import phidl.geometry as pg
import phidl.path as pp

def pad(size=[350, 350], wire_width=50, negative=True, trench=10, layer=2, metal_layer=12, shadow_layer=32, shadow_extra=20):
    size = np.array(size)
    stub_size = np.array([wire_width, wire_width/2])
    layer_device = Layer(layer, 1000)
    layer_metal = Layer(metal_layer, 1000)
    D = pg.flagpole(size=size, stub_size=stub_size, taper_type='fillet', layer=layer_device)
    D.move(-0.5 * size)
    D.remove(D.ports[2])
    if negative:
        D = pg.outline(D, distance=trench, open_ports=trench+1, layer=layer_device)
    R = pg.rectangle(size = size - 10, layer=layer_metal)
    R.move(-0.5 * (size - 10))
    D.add(R)
    SR = pg.rectangle(size=(R.xsize + shadow_extra, R.ysize + shadow_extra), layer=shadow_layer)
    SR.move(origin=SR.center, destination=(0,0))
    D.add(SR)
    return D

def fan(size=[100,50], wire_width=50, trench=10, layer=1):
    layer1 = Layer(layer, 1000)
    D = Device()
    P = pp.euler(radius=size[1], use_eff=True)
    P.append(pp.straight(length=size[0]-size[1]))
    segment = P.extrude(trench, layer=layer1)
    top = D.add_ref(segment)
    bottom = D.add_ref(segment)
    top.movey(0.5*wire_width+0.5*trench)
    bottom.mirror((0,0),(1,0))
    bottom.movey(-0.5*wire_width-0.5*trench)
    D.add_port(name='out', midpoint=[0,0], width=size[0]+wire_width, orientation=0)
    D.add_port(name='in', midpoint=[0,0], width=wire_width, orientation=180)
    return D
