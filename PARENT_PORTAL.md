# WorldForge Classroom — Family edition

## Run

```bash
export WORLDFORGE_TEACHER_CODE='your-private-teacher-code'
python3 server.py
```

Visit http://127.0.0.1:8080. Create an account and choose Student, Parent / Guardian, or Teacher. Set a unique teacher code before enabling teacher signup.

## Link parent and student
1. Student signs in and selects **Generate parent linking code** under Personal study goals.
2. Student shares the code with the parent. The code expires in 30 minutes and can be used once.
3. Parent signs in and enters the code in the Parent / guardian portal.
4. Parent can view that student's assignments, grades, feedback, and study goals. Parent can unlink the account at any time.

## New features
- Student study goals, completion tracking, and parent viewing
- Parent dashboard for multiple linked children
- Teacher classroom announcements visible to signed-in families
- Two additional themes: Slate and Rose Quartz
- Role-based API restrictions and integration tests

## Test

```bash
python3 -m unittest discover -s tests -p 'test_classroom.py' -v
node --check classroom.js
```

This is a trusted-local-network prototype, **not** a deployment-ready service for children's data. Before any public internet use, implement TLS, account verification, parent/guardian authorization and revocation policy, rate-limiting, backups, audit logs, and robust privacy/security review. Existing SQLite data in `classroom.sqlite3` is intentionally omitted from the ZIP; copy your database separately if upgrading a previous instance.
