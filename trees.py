#!/usr/bin/env python3

from phidl import Device, CrossSection
import phidl.geometry as pg
import phidl.path as pp

def branch_start(width=2, size=10, layer=2):
    D = Device()
    P1 = pp.Path()
    P1.append( pp.euler(angle=90,radius=size/2, use_eff=True) )
    P1.append( pp.euler(angle=-90,radius=size/2, use_eff=True) )
    P2 = pp.Path()
    P2.append( pp.euler(angle=-90,radius=size/2, use_eff=True) )
    P2.append( pp.euler(angle=90,radius=size/2, use_eff=True) )
    XS = CrossSection()
    XS.add(width=width, ports=('in', 'out'))
    bend1 = XS.extrude(P1)
    bend2 = XS.extrude(P2)
    D.add_ref([bend1,bend2])
    D.add_port(name='in', port=bend1.ports['in'])
    D.add_port(name='out1', port=bend1.ports['out'])
    D.add_port(name='out2', port=bend2.ports['out'])
    out = pg.boolean(D, None, operation = 'or', layer=layer)
    out.add_port(name='in', port=D.ports['in'])
    out.add_port(name='out1', port=D.ports['out1'])
    out.add_port(name='out2', port=D.ports['out2'])
    return out

def _choke(width, choke_width, choke_length, layer):
    CD = Device()
    C = pg.optimal_step(start_width=width, end_width=choke_width, symmetric=True, layer=layer)
    R = pg.compass((choke_length, choke_width), layer=layer)
    choke1 = CD.add_ref(C)
    choke2 = CD.add_ref(C)
    choke_bridge = CD.add_ref(R)
    choke_bridge.connect('W', choke1.ports[2])
    choke2.connect(2, choke_bridge.ports['E'])
    CD.add_port('in', port=choke1.ports[1])
    CD.add_port('out', port=choke2.ports[1])
    CN = pg.connector(midpoint=choke_bridge.center, width=choke_length, orientation=90)
    chan_ports = CD.add_ref(CN)
    CD.add_port(name='L', port=chan_ports.ports[1])
    CD.add_port(name='R', port=chan_ports.ports[2])
    CD.flatten()
    return CD

def tree_level(width=5, size=20, choke_width=1, choke_length=2, choke_dist=10, layer=2,
               layer_channel=12, negative=True, trench=2):
    if not negative:
        trench = 0
    D = Device()
    B = branch_start(width=width, size=size, layer=layer)
    branch = D.add_ref(B)

    C = _choke(width, choke_width, choke_length, layer)
    c_len = C.xsize

    choke1 = D.add_ref(C)
    choke1.connect('in', branch.ports['out1'])
    R1 = pg.straight(size=(width,c_len), layer=layer)
    rec1 = D.add_ref(R1)
    rec1.connect(1, branch.ports['out2'])

    R2 = pg.straight(size=(width, choke_dist), layer=layer)
    cbridge1 = D.add_ref(R2)
    cbridge2 = D.add_ref(R2)
    cbridge1.connect(1, choke1.ports['out'])
    cbridge2.connect(1, rec1.ports[2])

    choke2 = D.add_ref(C)
    choke2.connect('in', cbridge2.ports[2])
    rec2 = D.add_ref(R1)
    rec2.connect(1, cbridge1.ports[2])

    D.add_port(name='in', port=branch.ports['in'])
    D.add_port(name='out1', port=rec2.ports[2])
    D.add_port(name='out2', port=choke2.ports['out'])
    l1, r1 = choke1.ports['L'], choke1.ports['R']
    l2, r2 = choke2.ports['L'], choke2.ports['R']

    if negative:
        D = pg.outline(D, distance=trench, open_ports=trench+1, layer=layer)

    RS = pg.straight(size=(choke_length, width/2+trench), layer=layer_channel)
    ch1 = D.add_ref(RS)
    ch1.connect(1, l1)
    ch2 = D.add_ref(RS)
    ch2.connect(1, r2)
    RL = pg.straight(size=(choke_length, 2*size + width/2 + trench), layer=layer_channel)
    ch3 = D.add_ref(RL)
    ch3.connect(1, r1)
    ch4 = D.add_ref(RL)
    ch4.connect(1, l2)

    D.add_port(name='L1', port=ch1.ports[2])
    D.add_port(name='L2', port=ch4.ports[2])
    D.add_port(name='R1', port=ch3.ports[2])
    D.add_port(name='R2', port=ch2.ports[2])

    D.flatten()
    return D
