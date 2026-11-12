"""ANL logo geometry."""

import phidl.geometry as pg
import phidl.path as pp
from phidl import Device, Path


def _logo_base():
    """One arm of the three-fold symmetric logo path."""
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


def anl_logo(layer=1, scale=1):
    """Argonne National Laboratory logo, centered at the origin.

    Parameters
    ----------
    layer : int or Layer
        Fabrication layer to draw on.
    scale : float
        Magnification applied to the logo.

    Returns
    -------
    Device
        Flattened logo geometry (no ports).
    """
    out = Device()
    D = Device()
    P1 = _logo_base()
    P2 = _logo_base()
    P3 = _logo_base()
    P2.move(origin=(P2.xmax, P2.ymax), destination=(0, 0))
    P3.move(origin=(P3.xmin, P3.ymax), destination=(20, 0))
    P2.rotate(-120)
    P3.rotate(120, center=(20, 0))
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
    L = pg.union(D, layer=layer)
    L.move(origin=L.center, destination=(0, 0))
    logo = out.add_ref(L)
    logo.magnification = scale
    out.flatten()
    out.name = "Logo"
    return out
