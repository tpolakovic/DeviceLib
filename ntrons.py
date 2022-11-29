#!/usr/bin/env python3

from phidl import Device, Layer
import phidl.geometry as pg

def ntron(width = 10, choke = 5, gate = 1, negative = True, trench = 5, layer = 1):
    layer1 = Layer(layer, 1000)
    D = Device()
    C = pg.optimal_step(start_width = width, end_width = choke, layer = layer1)
    G = pg.optimal_step(start_width = width, end_width = gate, layer = layer1, symmetric = True, num_pts = 256)
    T = pg.tee(size = [gate*3, choke], stub_size = [gate, gate], layer = layer1, taper_type = 'fillet')

    top = D.add_ref(C)
    bottom = D.add_ref(C)
    mid = D.add_ref(T)
    gate = D.add_ref(G)

    bottom.mirror()
    mid.connect(2, top.ports[2])
    bottom.connect(2, mid.ports[1])
    gate.connect(2, mid.ports[3])
    D.add_port(name = 1, port = top.ports[1])
    D.add_port(name = 2, port = bottom.ports[1])
    D.add_port(name = 'gate', port = gate.ports[1])
    if negative:
        D = pg.outline(D, distance = trench, layer = layer1, open_ports = trench+1)
    return D
