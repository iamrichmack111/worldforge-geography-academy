# WorldForge Family Classroom — Getting started

## Start

```bash
cd worldforge
export WORLDFORGE_TEACHER_CODE='choose-a-long-private-code'
python3 server.py
```

Visit http://localhost:8080 and create accounts. Student, parent and teacher account creation all use the same signup screen. Teacher accounts require the invite code.

**Family workflow:** Create a student account, then sign in as that student and generate a parent linking code. Sign in as a parent and enter that code. The parent can now select the child, set homework with a due date, review the written submission and record a grade and feedback. The student sees this work alongside general geography assignments. Parents can link more than one child.

**Learning workflow:** Read a study-library card, open the 3D geography lab, explore and measure terrain, answer an assignment and submit it. The student can revise their response. Parents and teachers see progress appropriate to their roles. The geography terrain is *fictional*, so do not treat its distances or heights as real-world measurements.

## Tests

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

`test_controls.py` contains browser controls tests and may need Playwright. For the backend only:

```bash
python3 -m unittest discover -s tests -p 'test_classroom.py' -v
python3 -m unittest discover -s tests -p 'test_family_assignment.py' -v
```

## Persistence and upgrades

All account and homework information is in `classroom.sqlite3`, not in the ZIP. Back up your existing file before installing a new version. New tables are created on startup and existing data is retained when using the same database file. Stop the server before copying the database. Do not overwrite the old database with an empty one.

## Privacy / limitations

This is an **offline-first, local prototype**, not a production student information system. It does not include password resets, email verification, account recovery, school rostering, audit trails, rate limits, secure HTTPS hosting, or formal compliance controls. Do not expose it to the open internet or store sensitive child information until those are implemented. The 3D view requires online loading of its rendering library in the current build.
