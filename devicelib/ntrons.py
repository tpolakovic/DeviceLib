"""nTron-family superconducting switching devices.

Layer convention
----------------
The nTron variants wrap raw integer layers as ``Layer(layer, 1000)``: GDS
datatype 1000 marks the etch/trench convention used by the fabrication
flow. ``phidl.Layer`` objects passed through this wrapper keep their own
datatype, so layer stacks are unaffected.
"""

import numpy as np
import phidl.geometry as pg
from phidl import Device, Layer

# GDS datatype used to mark nTron etch geometry
_ETCH_DATATYPE = 1000


def _etch_layer(layer):
    """Apply the datatype-1000 etch convention to raw layer numbers."""
    return Layer(layer, _ETCH_DATATYPE)


def _tron_body(width, choke, gate, layer, notch=False):
    """Shared nTron assembly: two optimal-step leads joined by a tee with a gate lead.

    Parameters
    ----------
    width : float
        Width of the source/drain leads.
    choke : float
        Width of the constricted channel.
    gate : float
        Width of the gate lead.
    layer : Layer
        Fabrication layer.
    notch : bool
        If True, subtract a diamond notch from the tee crossbar.

    Returns
    -------
    Device
        Assembly with ports 1 (top lead), 2 (bottom lead), and 'gate'.
    """
    choke_eff = choke + (0.7071 * gate if notch else 0)
    D = Device()
    C = pg.optimal_step(start_width=width, end_width=choke_eff, layer=layer)
    G = pg.optimal_step(start_width=width, end_width=gate, layer=layer, symmetric=True, num_pts=256)
    T = pg.tee(size=[gate * 3, choke_eff], stub_size=[gate, gate], layer=layer, taper_type="fillet")
    if notch:
        T.movex(origin=T.x, destination=0)
        T.movey(-choke_eff)
        N = pg.rectangle(size=[gate * 1.5, gate * 1.5], layer=layer)
        N.move(origin=N.center, destination=[0, 0]).rotate(45)
        T2 = pg.boolean(T, N, "not", layer=layer)
        T2.add_port(port=T.ports[1], name=1)
        T2.add_port(port=T.ports[2], name=2)
        T2.add_port(port=T.ports[3], name=3)
        T = T2

    top = D.add_ref(C)
    bottom = D.add_ref(C)
    mid = D.add_ref(T)
    gate_ref = D.add_ref(G)

    bottom.mirror()
    mid.connect(2, top.ports[2])
    bottom.connect(2, mid.ports[1])
    gate_ref.connect(2, mid.ports[3])
    D.add_port(name=1, port=top.ports[1])
    D.add_port(name=2, port=bottom.ports[1])
    D.add_port(name="gate", port=gate_ref.ports[1])
    return D


def _outline_negative(D, trench, layer):
    """Trench outline used by the nTron variants."""
    return pg.outline(D, distance=trench, layer=layer, open_ports=trench + 1)


def ntron(width=10, choke=5, gate=1, negative=True, trench=5, layer=1):
    """Classic nTron: gate-controlled superconducting switch.

    Ports: 1 (top), 2 (bottom), 'gate'.

    Parameters
    ----------
    width : float
        Width of the source/drain leads.
    choke : float
        Width of the constricted channel.
    gate : float
        Width of the gate lead.
    negative : bool
        If True, add a trench outline around the device.
    trench : float
        Trench width when ``negative`` is True.
    layer : int or Layer
        Fabrication layer (raw ints get the datatype-1000 etch convention).
    """
    layer1 = _etch_layer(layer)
    D = _tron_body(width, choke, gate, layer1)
    if negative:
        D = _outline_negative(D, trench, layer1)
    return D


def notch_tron(width=10, choke=5, gate=1, negative=True, trench=5, layer=1):
    """nTron variant with a diamond notch cut into the tee crossbar.

    Ports: 1 (top), 2 (bottom), 'gate'. Parameters as in `ntron`.
    """
    layer1 = _etch_layer(layer)
    D = _tron_body(width, choke, gate, layer1, notch=True)
    if negative:
        D = _outline_negative(D, trench, layer1)
    return D


def dot_tron(
    width=10,
    choke=5,
    gate=1,
    negative=True,
    trench=5,
    layer=1,
    ndots=11,
    dot_size=0.25,
    dot_rows=3,
    dot_edge=0.75,
):
    """nTron variant with rows of dots subtracted across the channel.

    Ports: 1 (top), 2 (bottom), 'gate'.

    Parameters
    ----------
    ndots : int
        Number of dots per row.
    dot_size : float
        Radius of each dot.
    dot_rows : int
        Number of dot rows across the channel.
    dot_edge : float
        Rows span ``-dot_edge * choke`` to ``+dot_edge * choke``.

    Other parameters as in `ntron`.
    """
    layer1 = _etch_layer(layer)
    D = _tron_body(width, choke, gate, layer1)

    U = pg.boolean(D, None, "or", layer=layer1)
    U.add_port(name=1, port=D.ports[1])
    U.add_port(name=2, port=D.ports[2])
    U.add_port(name="gate", port=D.ports["gate"])
    U.movex(origin=U.x, destination=0)

    dot_poss = np.linspace(-width, width, ndots)
    row_poss = np.linspace(-dot_edge, dot_edge, dot_rows)
    dots = [
        pg.circle(radius=dot_size, layer=layer1).movex(x).movey((1 + y) * (choke / 2))
        for y in row_poss
        for x in dot_poss
    ]
    D2 = pg.boolean(U, dots, "not", layer=layer1)
    D2.add_port(name=1, port=U.ports[1])
    D2.add_port(name=2, port=U.ports[2])
    D2.add_port(name="gate", port=U.ports["gate"])

    if negative:
        D2 = _outline_negative(D2, trench, layer1)
    return D2


def viatron(
    width=10,
    choke=1,
    via=(0.8, 0.8),
    via_offset=0.5,
    gate_width=10,
    layer_channel=1,
    layer_via=2,
    layer_gate=3,
):
    """Via-gated nTron: gate couples to the channel through a via on a separate layer.

    Ports: 1 (south), 2 (north), 'gate' (west).

    Parameters
    ----------
    width : float
        Width of the source/drain leads.
    choke : float
        Size of the square channel conduction region.
    via : tuple of float
        (x, y) size of the via.
    via_offset : float
        Lateral offset of the via from the channel center.
    gate_width : float
        Width of the gate lead.
    layer_channel, layer_via, layer_gate : int or Layer
        Layers for the channel, via, and gate.
    """
    D = Device()
    centerpiece = D.add_ref(pg.compass(size=(choke, choke), layer=layer_channel))

    # Choke tapers
    S1 = pg.optimal_step(start_width=choke, end_width=width, layer=layer_channel)
    step_in = D.add_ref(S1)
    step_in.connect(1, centerpiece.ports["S"])
    step_out = D.add_ref(S1).mirror((0, 0), (1, 0))
    step_out.connect(1, centerpiece.ports["N"])
    D.add_port(name=1, port=step_in.ports[2])
    D.add_port(name=2, port=step_out.ports[2])

    # Via
    D.add_ref(pg.compass(size=via, layer=layer_via).movex(-via_offset))
    toppiece = D.add_ref(pg.compass(size=(choke, choke), layer=layer_gate).movex(-via_offset))

    # Gate
    gate = D.add_ref(
        pg.optimal_step(
            start_width=choke,
            end_width=gate_width,
            layer=layer_gate,
            symmetric=True,
            num_pts=100,
        )
    )
    gate.connect(1, toppiece.ports["W"])
    D.add_port(name="gate", port=gate.ports[2])

    return D
