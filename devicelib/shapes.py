"""Simple chip shapes: buses, Hall crosses, and e-beam stitching lines."""

import numpy as np
import phidl.geometry as pg
from phidl import Device


def bus(n=3, width=10, pitch=20, length=100, negative=True, trench=2, layer=2):
    """Array of ``n`` parallel straight wires.

    Ports are ``in_i`` (bottom) and ``out_i`` (top) for each wire ``i``.

    Parameters
    ----------
    n : int
        Number of wires.
    width : float
        Wire width.
    pitch : float
        Wire-to-wire pitch (may be negative to flip the array direction).
    length : float
        Wire length.
    negative : bool
        If True, add a trench outline around the wires.
    trench : float
        Trench width when ``negative`` is True.
    layer : int or Layer
        Fabrication layer.
    """
    D = Device()
    R = pg.straight(size=(width, length), layer=layer)
    for i in range(n):
        rect = D.add_ref(R)
        rect.movex(i * pitch)
        D.add_port(name=f"in_{i}", port=rect.ports[2])
        D.add_port(name=f"out_{i}", port=rect.ports[1])
    if negative:
        D = pg.outline(D, distance=trench, open_ports=width, layer=layer)
    return D


def hall_cross(width=2, length=10, connector_width=1, connector_length=2, trench=None, layer=None):
    """Hall bar cross: a channel with four voltage probes.

    Ports: ``channel_in``, ``channel_out``, ``probe_NW``, ``probe_SW``,
    ``probe_NE``, ``probe_SE``.

    Parameters
    ----------
    width : float
        Channel width.
    length : float
        Channel length.
    connector_width : float
        Width of the channel connectors and probes.
    connector_length : float
        Length of the channel connectors.
    trench : float or None
        If given, add a trench outline of this width around the cross.
    layer : int or Layer
        Fabrication layer.
    """
    D = Device()
    IC = pg.compass(size=(connector_width, width), layer=layer)
    C = pg.straight(size=(width, length), layer=layer)
    P = pg.straight(size=(connector_width, connector_length), layer=layer)

    channel_connector1 = D.add_ref(IC)
    channel_connector2 = D.add_ref(IC)
    channel = D.add_ref(C)
    channel.connect(1, channel_connector1.ports["E"])
    channel_connector2.connect("W", channel.ports[2])

    stub1 = D.add_ref(IC)
    stub2 = D.add_ref(IC)
    stub1.connect("E", channel_connector1.ports["W"])
    stub2.connect("W", channel_connector2.ports["E"])

    probe_NW = D.add_ref(P)
    probe_NW.connect(1, channel_connector1.ports["N"])
    probe_SW = D.add_ref(P)
    probe_SW.connect(1, channel_connector1.ports["S"])
    probe_NE = D.add_ref(P)
    probe_NE.connect(1, channel_connector2.ports["N"])
    probe_SE = D.add_ref(P)
    probe_SE.connect(1, channel_connector2.ports["S"])

    D.add_port(name="channel_in", port=stub1.ports["W"])
    D.add_port(name="channel_out", port=stub2.ports["E"])
    D.add_port(name="probe_NW", port=probe_NW.ports[2])
    D.add_port(name="probe_SW", port=probe_SW.ports[2])
    D.add_port(name="probe_NE", port=probe_NE.ports[2])
    D.add_port(name="probe_SE", port=probe_SE.ports[2])
    if trench:
        D = pg.outline(D, distance=trench, open_ports=width, layer=layer)
    return D


def stitches(device, source_layers, field_size=100, area=None, width=None, layer=0):
    """E-beam stitching lines for a write-field grid over ``device``.

    A grid of lines spaced by ``field_size`` (the write field) is intersected
    with the polygons of ``device`` on ``source_layers``, so stitching lines
    only appear where there is metal to stitch.

    Parameters
    ----------
    device : Device
        Device to stitch.
    source_layers : list of int or Layer
        Layers of ``device`` whose polygons receive stitching lines.
    field_size : float
        Write-field size (grid spacing).
    area : Device or None
        Device defining the extent of the grid; defaults to ``device`` itself.
    width : float or None
        Stitch line width; defaults to ``field_size / 20``.
    layer : int or Layer
        Layer the stitching lines are drawn on.
    """
    if width is None:
        width = field_size / 20
    grid = Device()
    rh = pg.rectangle((device.xsize, width))
    rv = pg.rectangle((width, device.ysize))
    grid_area = area if area is not None else device

    for x in np.arange(grid_area.xmin + field_size, grid_area.xmax, field_size):
        s = grid << rv
        s.movex(x - width / 2)
        s.movey(origin=s.y, destination=grid_area.y)
    for y in np.arange(grid_area.ymin + field_size, grid_area.ymax, field_size):
        s = grid << rh
        s.movey(y - width / 2)
        s.movex(origin=s.x, destination=grid_area.x)

    to_stitch = pg.extract(device, layers=source_layers)
    S = pg.boolean(to_stitch, grid, "and", layer=layer)
    S.name = "stitching"
    return S
