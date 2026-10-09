# WorldForge Geography Lab (3D edition)

## Run

From the `worldforge` directory:

```bash
python3 -m http.server 8080
```

Open **http://localhost:8080/geography3d.html**.

Three.js is loaded from jsDelivr; an internet connection is required to download its modules unless you vendor them locally. The terrain images and world metadata are local.

## Generate another world

```bash
python3 -m pip install -r requirements.txt
python3 worldforge.py --seed 777 --size 512 --rivers 30 --output output
```

Refresh the browser after generation. `worldforge.py` preserves the original 2D explorer at `viewer.html`.

## Geography lesson plan (30–45 minutes)

1. **5 minutes:** Orient yourself in the 3D terrain. Orbit and zoom. Predict the higher ridges.
2. **5 minutes:** Switch to elevation; compare different landforms. Change relief exaggeration to see why terrain displays can mislead.
3. **10 minutes:** Measure a topographic cross-section from a mountain to the ocean. Record high/low elevations and endpoint grade.
4. **5 minutes:** Identify a drainage divide and predict downhill runoff direction. Compare modeled river cells in the biome layer.
5. **5 minutes:** Compare temperature, moisture, and biome maps. Explain a hot, dry environment and a colder highland.
6. **5–10 minutes:** Complete the quiz and discuss simplifications.

## What is *not* scientifically accurate

- This is a **fictional procedural world**, not a map of Earth.
- The terrain heightmap is normalized. The software illustrates heights with `6000 * (normalized_height - sea_level)` metres, not surveyed elevation.
- One heightmap pixel is defined as **1 illustrative kilometre** for transect exercises.
- Generated temperature, moisture, and river routing are simplified classroom models and are **not** physically validated climate or hydrology.
- Coordinates on this world do not represent actual geographic coordinates; the latitude label is an educational convention.
- Caves in the original generator are a standalone cellular automaton, not geologically derived cave formations.

## Suggested next scientifically rigorous upgrade

Add a **real-world DEM mode** using publicly sourced digital elevation models (e.g. Copernicus DEM or USGS 3DEP), accompanied by projections, georeferencing, a scale bar and cited attribution. Keep the fictional generator as sandbox mode.
