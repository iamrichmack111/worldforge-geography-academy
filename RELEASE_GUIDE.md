# WorldForge one-command release kit

Requirements on your Ubuntu server: git, GitHub CLI (`gh`), ffmpeg, Python3/pip, Playwright browser dependencies, Docker Compose (optional but recommended), and outbound connectivity for Edge Neural TTS.

Run `gh auth login` once and ensure `gh auth status` works. **The release script creates a PUBLIC GitHub repository and uploads a demo video**. Review for sensitive content before you run it. Its screenshots show the logged-out/login page, a mountain lesson, and the 3D terrain; it does not log in as a student. No existing SQLite database is included, but you should still review your working folder before publication.

Single command after extracting: `bash release.sh`

Customize: `WORLDFORGE_REPO=my-geography-demo PORT=8032 WORLDFORGE_VOICE=en-US-JennyNeural bash release.sh`

The script captures screenshots, creates an H.264 demo using real screenshots, synthesizes narration (Edge TTS preferred), runs regression tests and pushes GitHub repo + demo release. It stops before publishing on most failures. It will not be able to produce voice if no TTS is available; Edge TTS requires internet access.

NOTE: releases are created with timestamped tags and README references the latest release. Do not use this unchanged project as a public children's service without security/privacy review.
