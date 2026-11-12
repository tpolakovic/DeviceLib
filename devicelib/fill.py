"""Hexagonal hole-array (fill) generation."""

import numpy as np
import phidl.geometry as pg
from phidl import Device


def hex_hole_array(avoid=None, box=None, a=10, radius=1, offset=10, layer=1):
    """Hexagonal array of holes that avoids the given device.

    The device (plus an outline of width ``offset``) is rasterized, and holes
    of radius ``radius`` are placed on a hexagonal lattice with lattice
    constant ``a`` wherever the raster is free. This replaces both the old
    ``hole_array`` (v1) and ``hex_Array`` (v2) helpers.

    Parameters
    ----------
    avoid : Device or None
        Device the array is made around. If None, ``box`` is required and a
        full array is generated inside it.
    box : array-like or None
        Bounding box of the array as ``[[xmin, ymin], [xmax, ymax]]``.
        Defaults to the bounding box of ``avoid``.
    a : float
        Lattice parameter (nearest-neighbour hole spacing).
    radius : float
        Radius of each hole.
    offset : float
        Keep-out distance between ``avoid`` and the nearest hole.
    layer : int or Layer
        Fabrication layer.

    Returns
    -------
    Device
        Device containing the hole array (no ports).
    """
    if avoid is None and box is None:
        raise ValueError("hex_hole_array needs at least one of 'avoid' or 'box'")
    if box is None:
        box = avoid.bbox
    box = np.array(box)

    R = Device("Hole Array")
    cir = pg.circle(radius, layer=layer)

    # Row spacing of the hexagonal lattice
    row_spacing = np.sin(np.pi / 3) * a

    # Keep-out region: the device plus an outline of width `offset`
    if avoid is not None:
        temp = Device("offset device")
        temp.add_ref(avoid)
        temp.add_ref(pg.outline(avoid, offset))
        shapes = temp.get_polygons()
    else:
        shapes = []

    # Raster cell size; `cells_per_hole` raster rows/cols per lattice site
    cells_per_hole = 2 * radius
    dX = a / cells_per_hole
    dY = 2 * row_spacing / cells_per_hole

    # Rasterize the keep-out region: False means the cell is free
    allowed1 = pg._rasterize_polygons(shapes, box, dX, dY)
    allowed2 = pg._rasterize_polygons(
        shapes, box + np.array([[a / 2, row_spacing], [0, 0]]), dX, dY
    )

    # Even lattice sites
    for row in range(np.size(allowed1, 0)):
        if row % cells_per_hole == 0:
            for col in range(np.size(allowed1, 1)):
                if col % cells_per_hole == 0 and not allowed1[row][col]:
                    hole = R.add_ref(cir)
                    hole.move(
                        destination=(
                            dX / 2 + int(col / cells_per_hole) * a,
                            dY / 2 + int(row / cells_per_hole) * 2 * row_spacing,
                        )
                    )

    # Odd (half-offset) lattice sites
    for row in range(np.size(allowed2, 0)):
        if row % cells_per_hole == 0:
            for col in range(np.size(allowed2, 1)):
                if col % cells_per_hole == 0 and not allowed2[row][col]:
                    hole = R.add_ref(cir)
                    hole.move(
                        destination=(
                            dX / 2 + a / 2 + int(col / cells_per_hole) * a,
                            dY / 2 + row_spacing + int(row / cells_per_hole) * 2 * row_spacing,
                        )
                    )

    return R
