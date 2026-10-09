# WorldForge V6 — connection and login fixes

- `PORT=8081` now works; default host `0.0.0.0` permits LAN devices to reach `family.local:8081`.
- Signup logs the new account in automatically. Existing accounts still use Login.
- Error message if the classroom API returns a broken response.
- 3D fallback displays the generated 2D biome map if Three.js or WebGL cannot load.
- No SQLite database included. Back up your previous `classroom.sqlite3` and copy it to this folder if migrating.

Launch: `PORT=8081 python3 server.py`
Visit: `http://family.local:8081`
Do not launch using `python -m http.server`, as login needs `server.py`.
