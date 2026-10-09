# WorldForge 3D — controls and regression tests

## In the app
Launch the app, allow the terrain to load, then click **Run control tests**. The results are displayed immediately above the location report. It checks rendering initialization, textures, inspect, map layers, relief, mode switches, transect, zero-distance transect, clearing, camera reset, lessons and quizzes.

The tests intentionally reset the view, quiz position and measurements. The quiz score increases by one during the test.

## Browser automation
From the `worldforge` directory:

```bash
python3 -m pip install pytest playwright
python3 -m playwright install chromium
python3 -m pytest -q tests/
```

The test suite starts its own local HTTP server, launches Chromium, clicks lesson and quiz controls, checks the score and validates the 3D fallback. It uses `/usr/bin/chromium` in CI; on a Mac, edit `executable_path` in `tests/test_controls.py` to use Playwright's installed Chromium instead if needed.

The WebGL view requires access to the Three.js CDN. When the library is unreachable, the app shows a static biome map and keeps the geography lessons and quiz functional.
