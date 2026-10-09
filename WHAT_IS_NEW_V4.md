# WorldForge V4 — Practice and learning progress

This builds on V3. It adds a server-graded geography practice area with 16 questions spread over eight topics. Each topic has two questions, explanations, and stored attempt history. Logged-in students can retake quizzes. Linked parents can see their children's practice history in the parent portal; unrelated accounts cannot see it.

## Running

```bash
export WORLDFORGE_TEACHER_CODE='choose-a-secret-code'
python3 server.py
```

Visit http://127.0.0.1:8080, sign up or log in as a student, and open **Geography knowledge checks**. As a parent, link your student using their generated code to see attempts.

## Testing

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
node --check classroom.js
```

This is a local teaching prototype: generated terrain is fictional, its units are illustrative, quizzes are introductory rather than comprehensive, and the service has not been security-audited for public hosting with minors' data. The 3D rendering and full click-by-click browser behavior still need verification on a browser with WebGL and the required external libraries available.

## Upgrading

Back up your existing `classroom.sqlite3`. Extract into a fresh directory, then copy `classroom.sqlite3` from your previous installation to the new one *with the server stopped*. On startup the new `practice_results` table is created without resetting accounts or homework.
