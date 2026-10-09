# WorldForge V11 — Daily Challenge and 100 Dark Themes

- Sign up/log in as student. The new Daily Challenge area grows from 5 questions on day one by one every calendar day, capped at 20 questions. Additional subject areas are introduced progressively. Day boundaries use UTC.
- Each student gets one server-graded daily submission. Results are stored in `daily_challenges` in the existing SQLite database. Streaks count consecutive completed days. No client clock can advance challenges.
- Theme chooser has 100 named dark combinations (10 backgrounds × 10 accents), with search. Selected theme persists in the browser.
- Classroom login redesigned with responsive split layout and CSS animation respecting reduced-motion preferences.

Start: `PORT=8031 python3 server.py` in this directory. Existing installations: back up `classroom.sqlite3` first and set `WORLDFORGE_DB` to your existing database path to keep your user accounts and work. Do not put unprotected classroom on public internet.
