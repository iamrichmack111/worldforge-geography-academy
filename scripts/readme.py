from pathlib import Path
p=Path('README.md');t=p.read_text()
block="""

## Screenshots & demo

![Python](https://img.shields.io/badge/Python-3.12-blue) ![Docker](https://img.shields.io/badge/Docker-Ready-2496ED) ![Tests](https://img.shields.io/badge/Tests-Unittest-informational) ![Playwright](https://img.shields.io/badge/Playwright-Screenshots-green)

The narrated demo video is attached to the latest [GitHub release](../../releases/latest).

| Classroom | Mountain quest | 3D geography |
|---|---|---|
| ![Classroom](media/screenshots/login.png) | ![Mountains](media/screenshots/mountains.png) | ![3D](media/screenshots/earth-3d.png) |

### Container

```bash
docker compose up --build -d
```

Open http://localhost:8032/classroom.html.

> For local educational use. Not security-hardened for public child accounts.
"""
marker='## Screenshots & demo'
if marker in t:t=t.split(marker)[0].rstrip()
p.write_text(t.rstrip()+block)
