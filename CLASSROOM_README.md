# WorldForge Classroom — Geography Homework Edition

A local classroom web application built on the existing procedural 3D geography explorer. All data stays in a SQLite database on the computer running `server.py`.

## Launch

```bash
cd worldforge
export WORLDFORGE_TEACHER_CODE='choose-a-private-classroom-invite-code'
python3 server.py
```

Open **http://127.0.0.1:8080/**. Do **not** use `python -m http.server` for the classroom; it serves static files and cannot run signup, login, or homework APIs.

Students select **Create account → Student**. Teachers select **Teacher** and enter the invite code you configured. Accounts are distinct; students cannot publish assignments or grade.

## Features

- Passwords are stored with salted PBKDF2 hashes, not plaintext.
- Login sessions use random HttpOnly, SameSite=Strict cookies with 7-day expiration.
- Four seeded geography homework exercises with due dates.
- Students can submit and edit written homework; edits reset previous grades.
- Teacher gradebook with feedback and scores 0–100.
- Five themes: Ocean, Forest, Desert, Atlas Light, Aurora. The chosen theme persists on the same browser and is shared with the 3D view.
- World data and the 3D lab from the original package remain available.

**Teaching note:** The 3D map is fictional. Use it to teach physical geography concepts, not to assess facts about a real place.

**Security:** This is intended for local, trusted-network use, not public hosting. For internet-facing deployment add HTTPS, rate limiting, account recovery, invitation lifecycle, backups, privacy controls, and administration. Set `WORLDFORGE_HOST=0.0.0.0` only if you deliberately want LAN access. Do not commit `classroom.sqlite3` to Git.

## Tests

```bash
python3 -m unittest discover -s tests -p 'test_classroom.py' -v
# Optional 3D browser controls suite (requires Playwright + Chromium):
python3 -m pytest -q tests/test_controls.py
```

## Files

`classroom.html`, `classroom.css`, `classroom.js`: frontend. `server.py`: static site + JSON auth/homework API. `classroom.sqlite3`: auto-created local user and homework database.
