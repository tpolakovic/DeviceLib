"""Nanowire devices: bridges, hairpins, SNSPD pixels, and SNAP structures."""

import numpy as np
import phidl.geometry as pg
from phidl import Device


def bridge(width=0.1, length=10, trench=0.25, layer=None, negative=True):
    """Straight nanowire bridge.

    Ports: 1 (west), 2 (east).

    Parameters
    ----------
    width : float
        Wire width.
    length : float
        Wire length.
    trench : float
        Trench width when ``negative`` is True.
    layer : int or Layer
        Fabrication layer.
    negative : bool
        If True, add a trench outline around the wire.
    """
    D = Device("Bridge")
    c = D.add_ref(pg.compass(size=(length, width), layer=layer))
    D.add_port(port=c.ports["W"], name=1)
    D.add_port(port=c.ports["E"], name=2)
    D.flatten()
    if negative:
        D = pg.outline(D, distance=trench, layer=layer, open_ports=trench + 10)
    return D


def hairpin(width=0.1, pitch=0.2, length=10, trench=0.25, turn_ratio=5, layer=None, negative=True):
    """Optimal hairpin nanowire.

    Ports: 1 and 2 (the two wire ends, both facing west).

    Parameters
    ----------
    width : float
        Wire width.
    pitch : float
        Wire pitch.
    length : float
        Length of the hairpin legs.
    trench : float
        Trench width when ``negative`` is True.
    turn_ratio : float
        Ratio of turn radius to wire width.
    layer : int or Layer
        Fabrication layer.
    negative : bool
        If True, add a trench outline around the wire.
    """
    D = Device("Hairpin")
    h = D.add_ref(
        pg.optimal_hairpin(
            width=width, pitch=pitch, length=length, turn_ratio=turn_ratio, layer=layer
        )
    )
    D.add_port(port=h.ports[1], name=1)
    D.add_port(port=h.ports[2], name=2)
    D.flatten()
    if negative:
        D = pg.outline(D, distance=trench, layer=layer, open_ports=True)
        D.ports[1].midpoint -= (trench, 0)
        D.ports[2].midpoint += (trench, 0)
    return D


def snspd(
    width=0.1,
    pitch=0.2,
    size=(10, 10),
    trench=0.25,
    connector_width=None,
    turn_ratio=5,
    layer=None,
    negative=True,
):
    """Superconducting nanowire single-photon detector pixel.

    Uses ``pg.snspd_expanded`` when ``connector_width`` is given, otherwise
    ``pg.snspd``. Ports: 1 and 2 (both facing west), moved to the origin.

    Parameters
    ----------
    width : float
        Wire width.
    pitch : float
        Wire pitch.
    size : tuple of float
        (x, y) size of the pixel.
    trench : float
        Trench width when ``negative`` is True.
    connector_width : float or None
        If given, expand the pixel connectors to this width.
    turn_ratio : float
        Ratio of turn radius to wire width.
    layer : int or Layer
        Fabrication layer.
    negative : bool
        If True, add a trench outline around the pixel.
    """
    D = Device("Pixel")
    if connector_width:
        W = pg.snspd_expanded(
            wire_width=width,
            wire_pitch=pitch,
            size=size,
            connector_width=connector_width,
            turn_ratio=turn_ratio,
            layer=layer,
        )
    else:
        W = pg.snspd(
            wire_width=width, wire_pitch=pitch, size=size, turn_ratio=turn_ratio, layer=layer
        )
    D.add_ref(W)
    D.add_port(1, port=W.ports[1])
    D.add_port(2, port=W.ports[2])
    D.flatten()
    if negative:
        D = pg.outline(D, distance=trench, layer=layer, open_ports=True)
        D.ports[1].midpoint -= (trench, 0)
        D.ports[2].midpoint += (trench, 0)
    D.move(origin=(D.xmin, D.ymin), destination=(0, 0))
    return D


def snspd_array(
    width=0.1,
    pitch=0.2,
    ch_width=1,
    size=(10, 10),
    n=(4, 4),
    negative=True,
    trench=0.25,
    turn_ratio=5,
    ch1_layer=None,
    ch2_layer=None,
    via_layer=None,
):
    """Multiplexed array of SNSPD pixels with two channel layers and vias.

    Ports: ``ColS_i`` / ``ColN_i`` per column and ``RowE_j`` / ``RowW_j`` per row.

    Parameters
    ----------
    width : float
        Wire width.
    pitch : float
        Wire pitch.
    ch_width : float
        Width of the routing channel wires.
    size : tuple of float
        (x, y) size of a single pixel cell.
    n : tuple of int
        (columns, rows) number of pixels.
    negative : bool
        If True, add trench outlines around pixel and routing layers.
    trench : float
        Trench width when ``negative`` is True.
    turn_ratio : float
        Ratio of turn radius to wire width.
    ch1_layer, ch2_layer, via_layer : int or Layer
        Layers for pixel/channel 1, channel 2, and the via between them.
    """
    if not negative:
        trench = 0
    D = Device()
    size = np.array(size)
    size = size - [3 * ch_width + trench, 2 * ch_width + trench]
    P = snspd(width, pitch, size, trench, turn_ratio=turn_ratio, layer=ch1_layer, negative=False)

    L1 = Device("Layer1")
    wirepix = L1.add_ref(P)

    T = pg.tee(
        size=(ch_width, ch_width),
        stub_size=(width, trench),
        taper_type="fillet",
        layer=ch1_layer,
    )
    tee1 = L1.add_ref(T)
    tee1.connect(3, wirepix.ports[1])
    R1 = pg.straight(size=(ch_width, size[1] + ch_width + trench), layer=ch1_layer)
    ch1ch = L1.add_ref(R1)
    ch1ch.connect(1, tee1.ports[2])
    tee2 = L1.add_ref(T)
    tee2.connect(3, wirepix.ports[2])
    teex, teey = tee2.xmax, tee2.ymax
    L1.add_port("L1N", port=tee1.ports[1])
    L1.add_port("L1S", port=ch1ch.ports[2])
    port_ = tee2.ports[2]
    if negative:
        L1 = pg.outline(L1, distance=trench, layer=ch1_layer, open_ports=trench)
    port_.orientation += 180
    L1.add_port("L2N", port=port_)
    lay1 = D.add_ref(L1)

    R2 = pg.rectangle(size=(ch_width * 0.8, ch_width * 0.8), layer=via_layer)
    via = D.add_ref(R2)
    via.move(origin=(via.xmax, via.ymax), destination=(teex, teey))
    via.move((-0.1 * ch_width, -0.1 * ch_width))

    L2 = Device("Layer2")
    R3 = pg.straight(size=(ch_width, ch_width), layer=ch2_layer)
    ch2via = L2.add_ref(R3)
    ch2via.connect(2, lay1.ports["L2N"])
    R4 = pg.compass(size=(ch_width, ch_width), layer=ch2_layer)
    ch2tee = L2.add_ref(R4)
    ch2tee.connect("N", ch2via.ports[1])
    R5 = pg.straight(size=(ch_width, size[0] + 2 * ch_width), layer=ch2_layer)
    ch2ch = L2.add_ref(R5)
    ch2ch.connect(2, ch2tee.ports["W"])
    R6 = pg.straight(size=(ch_width, trench), layer=ch2_layer)
    ch2cap = L2.add_ref(R6)
    ch2cap.connect(1, ch2tee.ports["E"])
    L2.add_port("L2E", port=ch2ch.ports[1])
    L2.add_port("L2W", port=ch2cap.ports[2])
    if negative:
        L2 = pg.outline(L2, distance=trench, layer=ch2_layer, open_ports=trench)
    lay2 = D.add_ref(L2)
    D.add_port("N", port=lay1.ports["L1N"])
    D.add_port("S", port=lay1.ports["L1S"])
    D.add_port("E", port=lay2.ports["L2E"])
    D.add_port("W", port=lay2.ports["L2W"])
    D.flatten()
    D.move(origin=(D.xmin, D.ymin), destination=(0, 0))

    A = Device("Pixel_Array")
    arr = A.add_array(D, columns=n[0], rows=n[1], spacing=(D.xsize, D.ysize))
    for i in range(arr.columns):
        A.add_port(
            name=f"ColS_{i}",
            midpoint=(D.ports["S"].midpoint[0] + i * D.xsize, D.ports["S"].midpoint[1]),
            width=ch_width,
            orientation=-90,
        )
        A.add_port(
            name=f"ColN_{i}",
            midpoint=(
                D.ports["S"].midpoint[0] + i * D.xsize,
                D.ports["N"].midpoint[1] + (arr.rows - 1) * D.ysize,
            ),
            width=ch_width,
            orientation=90,
        )
    for j in range(arr.rows):
        A.add_port(
            name=f"RowE_{j}",
            midpoint=(D.ports["E"].midpoint[0], D.ports["E"].midpoint[1] + j * D.ysize),
            width=ch_width,
            orientation=180,
        )
        A.add_port(
            name=f"RowW_{j}",
            midpoint=(
                D.ports["W"].midpoint[0] + (arr.columns - 1) * D.xsize,
                D.ports["W"].midpoint[1] + j * D.ysize,
            ),
            width=ch_width,
            orientation=0,
        )
    return A


def half_hairpin(width=0.1, pitch=0.2, length=10, turn_ratio=4, num_pts=50, layer=None):
    """Half of an optimal hairpin: one turn plus a straight tail (borrowed from PHIDL).

    Port: 1 (west, at the origin).
    """
    a = (pitch + width) / 2
    y = -(pitch - width) / 2
    x = -pitch
    dl = width / (num_pts * 2)
    n = 0

    xpts = [x]
    ypts = [y]
    while (y < 0) & (n < 1e6):
        s = x + 1j * y
        w = np.sqrt(1 - np.exp(np.pi * s / a))
        wx = np.real(w)
        wy = np.imag(w)
        wx = wx / np.sqrt(wx**2 + wy**2)
        wy = wy / np.sqrt(wx**2 + wy**2)
        x = x + wx * dl
        y = y + wy * dl
        xpts.append(x)
        ypts.append(y)
        n = n + 1
    ypts[-1] = 0  # Set last point be on the x=0 axis for sake of cleanliness
    ds_factor = int(len(xpts) / num_pts)  # Downsample the total number of points
    xpts = xpts[::-ds_factor]
    xpts = xpts[::-1]  # This looks confusing, but it's just flipping the arrays around
    ypts = ypts[::-ds_factor]
    ypts = ypts[::-1]  # so the last point is guaranteed to be included when downsampled

    # Add points for the rest of meander
    xpts.append(xpts[-1] + turn_ratio * width)
    ypts.append(0)
    xpts.append(xpts[-1])
    ypts.append(-a)
    xpts.append(xpts[0])
    ypts.append(-a)
    xpts.append(max(xpts) - length)
    ypts.append(-a)
    xpts.append(xpts[-1])
    ypts.append(-a + width)
    xpts.append(xpts[0])
    ypts.append(ypts[0])

    xpts = np.array(xpts)
    ypts = np.array(ypts)

    D = Device(name="hairpin")
    D.add_polygon([xpts, ypts], layer=layer)
    D.move(origin=(D.xmin, D.ymin), destination=(0, -width / 2))
    D.add_port(name=1, midpoint=(0, 0), width=width, orientation=180)
    return D


def mid_hairpin(width=0.1, pitch=0.2, length=10, turn_ratio=4, num_pts=50, layer=None):
    """Two mirrored half-hairpins unioned into an S-shaped middle segment.

    Port: 1 (west, at the origin).
    """
    D = Device()
    H1 = half_hairpin(width, pitch, length, turn_ratio, num_pts, layer)
    D.add_ref(H1)
    h2 = D.add_ref(H1)
    h2.mirror((0, 0), (1, 0))
    D = pg.boolean(D, None, operation="or", layer=layer)
    D.movex(origin=D.xmin, destination=0)
    D.add_port(name=1, midpoint=(0, 0), width=width, orientation=180)
    return D


def turn_comb(
    width=0.1, pitch=0.2, length=10, n=3, turn_ratio=4, num_pts=50, layer=None, extra_cap=None
):
    """Stack of ``n`` hairpin turns forming a comb with all ports on one side.

    Ports: 1..n (west side, bottom to top) and ``cap`` (east side).

    Parameters
    ----------
    extra_cap : float or None
        If given, extend the east side with a cap bar of this length.
    """
    D = Device()

    B = half_hairpin(width, pitch, length, turn_ratio, num_pts, layer)
    M = mid_hairpin(width, pitch, length, turn_ratio, num_pts, layer)

    bottom = D.add_ref(B)
    bottom.movey(origin=bottom.ymin, destination=0)
    D.add_port(port=bottom.ports[1], name=n)
    for i in range(n - 2):
        ym = D.ymax
        m = D.add_ref(M)
        m.movey(origin=m.ymin, destination=ym)
        D.add_port(port=m.ports[1], name=(n - i - 1))
    top = D.add_ref(B)
    top.mirror((0, 0), (1, 0))
    top.movey(origin=top.ymin, destination=D.ymax)
    D.add_port(port=top.ports[1], name=1)
    D.add_port(name="cap", midpoint=(D.xmax, D.ymax / 2), width=D.ysize, orientation=0)
    if extra_cap:
        C = pg.compass(size=(extra_cap, D.ysize), layer=layer)
        cap = D.add_ref(C)
        cap.connect(port="W", destination=D.ports["cap"])
        D.remove(D.ports["cap"])
        D.add_port(name="cap", port=cap.ports["E"])

    return D


def snap_segment(width=0.1, pitch=0.2, length=10, n=3, turn_ratio=4, num_pts=50, layer=None):
    """Two mirrored turn combs forming one SNAP segment.

    Ports: 1 (east), 2 (west) — the two ``cap`` ends.
    """
    D = Device()
    S = turn_comb(width, pitch, length / 2, n, turn_ratio, num_pts, layer)
    s1 = D.add_ref(S)
    s2 = D.add_ref(S)
    s2.mirror((0, 0), (0, 1))
    D.add_port(name=1, port=s2.ports["cap"])
    D.add_port(name=2, port=s1.ports["cap"])
    return D


def snap_line(width=0.1, pitch=0.2, length=10, n=3, n_segs=3, turn_ratio=4, num_pts=50, layer=None):
    """``n_segs`` SNAP segments chained into a straight line.

    Ports: 1 and 2 (the two ends).
    """
    D = Device()
    S = snap_segment(width, pitch, length, n, turn_ratio, num_pts, layer)
    s1 = D.add_ref(S)
    D.add_port(name=1, port=s1.ports[1])
    for _ in range(n_segs - 1):
        s2 = D.add_ref(S)
        s2.connect(1, s1.ports[2])
        s1 = s2
    D.add_port(name=2, port=s1.ports[2])
    return D


def snap_turn(width=0.1, pitch=0.2, length=10, n=3, turn_ratio=4, num_pts=50, layer=None):
    """90-degree turn between two SNAP lines.

    Ports: 1 and 2 (the two ``cap`` ends).
    """
    LT = Device()

    TC = turn_comb(width, pitch, length / 2, n * 2, turn_ratio, num_pts, layer, width * n)
    STC = turn_comb(width, pitch, length / 2, n, turn_ratio, num_pts, layer)
    turn = LT.add_ref(TC)
    top = LT.add_ref(STC)
    bottom = LT.add_ref(STC)
    bottom.connect(1, turn.ports[n * 2])
    top.connect(n, turn.ports[1])
    LT.add_port(name=1, port=bottom.ports["cap"])
    LT.add_port(name=2, port=top.ports["cap"])
    return LT


def snap(
    width=0.1,
    pitch=0.2,
    size=(10, 10),
    n=3,
    n_segs=3,
    turn_ratio=4,
    num_pts=50,
    layer=None,
    trench=0.2,
    negative=True,
):
    """Series nanowire avalanche photon detector: SNAP meander folded to fill ``size``.

    Ports: 1 and 2 (east side), centered at the origin.

    Parameters
    ----------
    size : tuple of float
        (x, y) outer size the meander is folded into.
    n : int
        Number of wires per SNAP segment.
    n_segs : int
        Number of segments per horizontal run.
    trench : float
        Trench width when ``negative`` is True.
    negative : bool
        If True, add a trench outline around the meander.
    """
    seg_length = size[0] / n_segs
    D = Device()
    L = snap_line(width, pitch, seg_length, n, n_segs - 2, turn_ratio, num_pts, layer)

    LT = snap_turn(width, pitch, seg_length, n, turn_ratio, num_pts, layer)
    t1 = D.add_ref(LT)
    t2 = D.add_ref(LT)
    l1 = D.add_ref(L)
    t1.connect(1, l1.ports[2])
    t2.connect(1, l1.ports[1])
    l2 = D.add_ref(L)
    l2.connect(2, t2.ports[2])
    D.add_port(1, port=l2.ports[1])
    D.add_port(2, port=t1.ports[2])

    S = Device()
    m1 = S.add_ref(D)
    start = S.add_ref(snap_segment(width, pitch, seg_length, n, turn_ratio, num_pts, layer))
    start.connect(2, m1.ports[1])
    while S.ysize < size[1]:
        m2 = S.add_ref(D)
        m2.connect(1, m1.ports[2])
        m1 = m2
    stop = S.add_ref(snap_line(width, pitch, seg_length, n, n_segs - 1, turn_ratio, num_pts, layer))
    stop.connect(1, m1.ports[2])
    C = pg.compass((width * n, L.ysize), layer)
    cstop = S.add_ref(C)
    cstop.connect("E", stop.ports[2])
    cstart = S.add_ref(C)
    cstart.connect("W", start.ports[1])
    S.add_port(1, port=cstop.ports["W"])
    S.add_port(2, port=cstart.ports["E"])
    S.move(S.center, (0, 0))
    if negative:
        S = pg.outline(S, distance=trench, open_ports=True, layer=layer)
        S.ports[2].midpoint[0] += trench
        S.ports[1].midpoint[0] -= trench

    return S


def ps_junction(width1=1, width2=1, widthj=0.05, length=1):
    """Proximity-effect superconductor-semiconductor junction.

    Two symmetric optimal steps joined by a narrow constriction.
    Ports: 1 and 2 (the wide ends).
    """
    D = Device()
    s1 = D.add_ref(pg.optimal_step(end_width=width1, start_width=widthj, symmetric=True))
    s2 = D.add_ref(pg.optimal_step(end_width=width2, start_width=widthj, symmetric=True))
    junction = D.add_ref(pg.straight((widthj, length)))
    s1.connect(1, junction.ports[1])
    s2.connect(1, junction.ports[2])
    D.add_port(1, port=s1.ports[2])
    D.add_port(2, port=s2.ports[2])
    D.flatten()
    return D


def charge_island():
    """Charge island: two back-to-back ``ps_junction`` devices with a gate tap."""
    D = Device()
    P = ps_junction(width1=1, width2=4)
    psj1 = D.add_ref(P)
    psj2 = D.add_ref(P)
    psj1.connect(1, psj2.ports[1])

    D.move(origin=D.center, destination=(0, 0))
    D.rotate(90)

    tap = D.add_ref(pg.taper(5, 10, 3))
    tap.rotate(-90)
    tap.movey(6)

    return D
