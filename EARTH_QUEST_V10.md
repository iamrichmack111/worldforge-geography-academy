# WorldForge V10 — Earth Explorer Quest

* Three separate teaching diagrams: mountains, terrain, Earth layers.
* 12 clickable questions per unit, 36 total.
* Keyboard-accessible spot shortcuts, immediate answers, and per-unit saved progress.
* Earth diagrams and spot positions are schematic and **not to scale**; distances/depths are described in explanations.
* The quest is standalone and does not modify student homework or grades.

Run: `PORT=8031 python3 server.py` and open `/landform-quest.html`.

Test with `node --check landform-quest.js`, `node --check landform-data.js`, and `python3 -m unittest discover -s tests -p 'test_*.py'` (Playwright browser tests require local Chromium).
