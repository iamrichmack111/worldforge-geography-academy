# WorldForge V12 — Visual rebuild

This release replaces the V11 login shell with a full-screen two-column sign-in, globe illustration, responsive layout, sidebar classroom navigation, and a 100-palette swatch browser. All old routes, lessons, homework, and API handling are retained.

Run with `PORT=8032 python3 server.py` from this directory. Visit `http://family.local:8032/classroom.html?v=12` and hard-refresh with Ctrl+Shift+R.

If the page still looks old, confirm the active server process is running this extracted directory rather than V11. Protect and copy your previous classroom.sqlite3 if you need to retain account data.
