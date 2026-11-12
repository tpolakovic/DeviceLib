"""Alignment marker geometries."""

import phidl.geometry as pg
from phidl import Device


def alignment_marks(layer=1):
    """Nested cross alignment marks (large cross with medium and small corner crosses).

    Parameters
    ----------
    layer : int or Layer
        Fabrication layer to draw on.

    Returns
    -------
    Device
        Unioned alignment mark geometry (no ports).
    """
    D = Device(name="Alignment")
    CB = pg.cross(length=50, width=5)
    CM = pg.cross(length=10, width=1)
    CS = pg.cross(length=5, width=0.5)

    # Small crosses at three corners of the medium cross
    def _corners(bbox):
        return [
            (bbox[1, 1], bbox[1, 1]),
            (bbox[1, 1], bbox[0, 1]),
            (bbox[0, 1], bbox[0, 1]),
            (bbox[0, 0], bbox[1, 1]),
        ]

    for corner in _corners(CM.bbox):
        small = CM.add_ref(CS)
        small.move(origin=small.center, destination=corner)

    # Medium crosses at three corners of the large cross
    for corner in _corners(CB.bbox):
        med = CB.add_ref(CM)
        med.move(origin=med.center, destination=corner)

    D.add_ref(CB)
    D = pg.union(D, layer=layer)
    D.name = "AlignmentMarks"
    return D
