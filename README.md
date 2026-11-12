# DeviceLib

Library for quick design of superconducting device chips, built on
[PHIDL](https://github.com/amccaugh/phidl). Example usage can be found
[here](https://eicweb.phy.anl.gov/-/snippets/54).

## Install

```bash
git clone git@eicweb.phy.anl.gov:nanowire/fabrication/devicelib.git DeviceLib
cd DeviceLib
pip install -e .
```

Requires Python >= 3.9, `phidl >= 1.6`, and `numpy`.

## Usage

Every device function returns a PHIDL `Device` with standardized ports:
numbered ports (`1`, `2`, ...) for main connections and named ports
(`'gate'`, `'in'`, `'out'`, ...) for special ones.

```python
from devicelib import snspd, pad, ntron

D = snspd(width=0.15, pitch=0.3, size=(20, 20), layer=1)
P = pad(size=(350, 350), layer=2)
N = ntron(width=10, choke=5, gate=1, layer=3)

D.connect(1, P.ports[1])
D.write_gds("pixel.gds")
```

Most device functions support a `negative` parameter: `negative=True` adds a
trenched outline of width `trench` around the device.

## Modules

| Module             | Contents                                                        |
|--------------------|-----------------------------------------------------------------|
| `devicelib.ntrons` | `ntron`, `notch_tron`, `dot_tron`, `viatron`                    |
| `devicelib.nwires` | `bridge`, `hairpin`, `snspd`, `snspd_array`, SNAP family, `ps_junction`, `charge_island` |
| `devicelib.pads`   | `pad`, `launchpad`, `fan`                                       |
| `devicelib.trees`  | `tree` (binary multiplexing readout tree)                       |
| `devicelib.shapes` | `bus`, `hall_cross`, `stitches` (e-beam stitching lines)        |
| `devicelib.fill`   | `hex_hole_array` (hexagonal hole filling around devices)        |
| `devicelib.markers`| `alignment_marks`                                               |
| `devicelib.logo`   | `anl_logo`                                                      |

All public functions are also re-exported at the top level, so
`from devicelib import snspd` and `from devicelib.nwires import snspd`
are equivalent.

### Layer conventions

- `layer` parameters accept anything PHIDL accepts (int, tuple, or `Layer`).
  Layers default to `None` where unused; no geometry is drawn for `None`
  metal/shadow layers.
- The nTron family and `fan` wrap raw integer layers as `Layer(layer, 1000)`:
  GDS datatype 1000 marks the etch convention used in the fabrication flow.
  `Layer` objects pass through with their own datatype.

## Development

```bash
pip install -e ".[dev]"   # or: pip install ruff pytest
ruff format . && ruff check .
pytest
```

Tests are intentionally minimal smoke tests for now; broader coverage will
come from the outside driving (wafer layout) scripts.

When adding new devices:

1. Return a PHIDL `Device` with appropriate ports for connectivity.
2. Support both positive and negative geometry modes where applicable, using
   the common parameter names `width`, `layer`, `negative`, `trench`.
3. Add the function to `devicelib/__init__.py` (`__all__`) and to a smoke test.

## License

GPL-3.0-or-later. See [LICENSE](LICENSE).
