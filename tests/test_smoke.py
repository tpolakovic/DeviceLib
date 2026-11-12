"""Minimal smoke tests: the package imports and representative devices build.

Broader coverage will come from the outside driving scripts as they are
migrated to devicelib.
"""

import pytest

import devicelib as dl


def test_package_exports():
    assert dl.__version__
    for name in dl.__all__:
        assert hasattr(dl, name), f"missing export: {name}"


def test_representative_devices_build():
    devices = {
        "ntron": dl.ntron(layer=1),
        "dot_tron": dl.dot_tron(layer=1),
        "snspd": dl.snspd(layer=1),
        "pad": dl.pad(layer=1, metal_layer=2, shadow_layer=3),
        "tree": dl.tree(n_levels=2),
        "alignment_marks": dl.alignment_marks(layer=1),
        "anl_logo": dl.anl_logo(layer=1),
    }
    for name, D in devices.items():
        assert D.get_polygons(), f"{name} produced empty geometry"


def test_ports_present():
    assert set(dl.ntron(layer=1).ports) >= {1, 2, "gate"}
    assert set(dl.snspd(layer=1).ports) >= {1, 2}
    assert set(dl.tree(n_levels=1).ports) >= {"in", "out_0", "out_1"}


def test_hex_hole_array():
    pytest.importorskip("skimage", reason="phidl rasterization requires scikit-image")
    D = dl.hex_hole_array(box=[[0, 0], [50, 50]], a=10, radius=1)
    assert D.get_polygons()
