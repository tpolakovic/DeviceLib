"""DeviceLib: quick design of superconducting device chips, built on PHIDL.

All public device functions are re-exported here, so the recommended import
style is::

    from devicelib import snspd, pad, ntron

Every function returns a PHIDL ``Device`` with standardized ports (numbered
ports for main connections, named ports like 'gate' for special ones).
"""

from devicelib.fill import hex_hole_array
from devicelib.logo import anl_logo
from devicelib.markers import alignment_marks
from devicelib.ntrons import dot_tron, notch_tron, ntron, viatron
from devicelib.nwires import (
    bridge,
    charge_island,
    hairpin,
    half_hairpin,
    mid_hairpin,
    ps_junction,
    snap,
    snap_line,
    snap_segment,
    snap_turn,
    snspd,
    snspd_array,
    turn_comb,
)
from devicelib.pads import fan, launchpad, pad
from devicelib.shapes import bus, hall_cross, stitches
from devicelib.trees import tree

__version__ = "0.1.0"

__all__ = [
    # ntrons
    "ntron",
    "notch_tron",
    "dot_tron",
    "viatron",
    # nanowires
    "bridge",
    "hairpin",
    "snspd",
    "snspd_array",
    "half_hairpin",
    "mid_hairpin",
    "turn_comb",
    "snap_segment",
    "snap_line",
    "snap_turn",
    "snap",
    "ps_junction",
    "charge_island",
    # pads
    "pad",
    "launchpad",
    "fan",
    # trees
    "tree",
    # shapes, fill, markers, logo
    "bus",
    "hall_cross",
    "stitches",
    "hex_hole_array",
    "alignment_marks",
    "anl_logo",
    "__version__",
]
