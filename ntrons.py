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

def viatron(width = 10, choke = 1, via = (0.8, 0.8), via_offset=0.5, gate_width = 10, trench = None,
            layer_channel = 1, layer_via = 2, layer_gate = 3):
    D = Device()
    centerpiece = D.add_ref(
        pg.compass(size = (choke, choke), layer = layer_channel)
    )

    # Choke tapers
    S1 = pg.optimal_step(start_width = choke, end_width = width, layer = layer_channel)
    step_in = D.add_ref(S1)
    step_in.connect(1, centerpiece.ports['S'])
    step_out = D.add_ref(S1).mirror((0, 0), (1, 0))
    step_out.connect(1, centerpiece.ports['N'])
    D.add_port(name = '1', port = step_in.ports[2])
    D.add_port(name = '2', port = step_out.ports[2])

    # Via
    via = D.add_ref(
        pg.compass(size = via, layer = layer_via).movex(-via_offset)
    )
    toppiece = D.add_ref(
        pg.compass(size = (choke, choke), layer = layer_gate).movex(-via_offset)
    )

    # Gate
    gate = D.add_ref(
        pg.optimal_step(start_width = choke, end_width = gate_width,
                        layer = layer_gate, symmetric = True, num_pts = 100)
    )
    gate.connect(1, toppiece.ports['W'])
    D.add_port(name='gate', port = gate.ports[2])
    
    return D