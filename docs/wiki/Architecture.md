# Architecture

- `server.py`: Python server and student/parent/teacher APIs
- `classroom.html`, `.js`, `.css`: classroom experience
- `geography3d.html`: Three.js-based generated terrain explorer
- `landform-quest.html`: interactive mountain, terrain and Earth-layer spots
- SQLite: local users, assignments, grades and progress
- `Dockerfile`, `compose.yaml`: self-hosted service and persistent storage
- `.github/workflows/ci-cd.yml`: tests and GHCR container builds

Keep databases and private credentials out of commits, releases and screenshots.
