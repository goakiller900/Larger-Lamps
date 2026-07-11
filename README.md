# Larger Lamps 2.1

Community-maintained continuation of Deadlock's Larger Lamps for Factorio 2.1.

## Features

- **Large lamp** — a 2×2 electric lamp with a wide, soft glow and circuit-network colour control.
- **Copper lamp** — a 2×2 burner lamp that consumes chemical fuel.
- **Electric copper lamp** — an electric, circuit-compatible version of the copper lamp.
- **Floor lamp** — a 2×2 electric floor panel that players and vehicles can cross.

## Compatibility

- Factorio 2.1
- Space Age can be enabled, but is not required.
- AAI Industry 0.7.0 or newer is supported as an optional dependency.

AAI compatibility changes recipe ingredients while keeping standard Factorio crafting categories. The compatibility layer does not patch or depend on specific AAI machine prototype names.

## Source layout

The playable mod source is stored in [`LargerLamps-2.0/`](LargerLamps-2.0/). Release archives are generated from that directory and use the internal mod name and version from `info.json`.

## Building a release

```bash
python scripts/build_release.py
```

This creates a deterministic Factorio-ready ZIP and SHA-256 checksum in `dist/`.

## Credits

- **Deadlock989** — original Larger Lamps design, code and graphics.
- **goakiller900** — current continuation and maintenance.
- **MasterBuilder**, **NullHarp**, **Teppy381**, **ChocoMaxXx**, **Kamsta99**, **odnols**, and other contributors — fixes, translations, graphics and testing.

## License

GNU General Public License version 3 or later. See [LICENSE](LICENSE) and the retained notice in [`LargerLamps-2.0/license.txt`](LargerLamps-2.0/license.txt).
