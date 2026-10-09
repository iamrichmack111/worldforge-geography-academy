# WorldForge — Procedural World Generator

Seeded, offline 2D world generation with terrain elevation, temperature, moisture, biomes, rivers, lakes, and an underground cave layer.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Generate a world

```bash
python worldforge.py --seed 2026 --size 512 --rivers 35 --output output
```

Change `--seed` to generate a different world. The same seed and settings generate the same map with the same NumPy version. `--sea-level` changes how much terrain is underwater.

## Outputs

- `world.png` — colored biome map
- `elevation.png`, `moisture.png`, `temperature.png` — grayscale simulation layers
- `caves.png` — underground cave system
- `world.npz` — numerical layers for future simulation and game development
- `world.json` — metadata and biome counts

## Roadmap

- Downhill flow accumulation for connected river networks and large drainage basins
- Erosion and sediment transport
- 3D terrain mesh export (OBJ/glTF)
- Town placement, roads, and evolving civilization simulation
- Chunked/infinite world generation

## Notes

This is a 2D heightmap-based world model, not a photorealistic 3D renderer. Rivers use simple local downhill tracing (some will end in inland basins). The cave layer is independently generated using cellular automata.

## Interactive map viewer

Run this from the project folder:

```bash
python3 -m http.server 8080
```

Visit http://localhost:8080/viewer.html to zoom, pan, and switch between terrain, temperature, moisture, elevation, and cave maps. The viewer reads files from `output/` (a pre-generated seed 2026 is included). Re-run the generator with `--output output`, then refresh the page to view another world.

## 3D geography lessons

Run `python3 -m http.server 8080`, then open [Geography Lab](http://localhost:8080/geography3d.html). See `GEOGRAPHY_3D_README.md` for guided exercises, quiz content, and model limitations.

## Screenshots & demo

![Python](https://img.shields.io/badge/Python-3.12-blue) ![Docker](https://img.shields.io/badge/Docker-Ready-2496ED) ![Tests](https://img.shields.io/badge/Tests-Unittest-informational) ![Playwright](https://img.shields.io/badge/Playwright-Screenshots-green)

The narrated demo video is attached to the latest [GitHub release](../../releases/latest).

| Classroom | Mountain quest | 3D geography |
|---|---|---|
| ![Classroom](media/screenshots/login.png) | ![Mountains](media/screenshots/mountains.png) | ![3D](media/screenshots/earth-3d.png) |

### Container

```bash
docker compose up --build -d
```

Open http://localhost:8032/classroom.html.

> For local educational use. Not security-hardened for public child accounts.
