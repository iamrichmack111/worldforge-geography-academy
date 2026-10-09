# WorldForge V5 — Classroom redesign & continents

## Changes
- New streamlined classroom visuals: editorial hero, clear section navigation, spacious quiz layout, updated theme palette.
- 15 geography question areas × 5 questions = 75 total.
- Added continent topics: Africa, Antarctica, Asia, Europe, North America, South America, Australia and Oceania (seven-continent model).
- Added short reference cards for each continent in the study library.
- Parent/student accounts, teacher homework, grading and 3D fictional terrain remain available.
- Continent cards link to OpenStreetMap, an external real-world map requiring internet access. The local 3D world is still fictional and should not be used to locate real continents.

## Start
```bash
python3 server.py
```
Visit http://localhost:8080. See START_HERE.md for detailed instructions.

## Test
```bash
python3 -m unittest discover -s tests -p 'test_*.py' -q
```
There are 8 backend unit/integration tests; browser-based 3D tests require Playwright and browser binaries. Full live browser verification was not completed here.

## Existing data
Back up classroom.sqlite3 before replacing an older installation. Preserve your existing classroom.sqlite3 and do not overwrite it with a fresh install. Quiz questions are built in code and do not require a database migration.
