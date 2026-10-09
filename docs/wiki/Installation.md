# Installation

## Docker

```bash
PORT=8032 docker compose up --build -d
```

Visit http://localhost:8032/classroom.html or http://family.local:8032/classroom.html on a reachable LAN.

## Python

```bash
python3 -m pip install -r requirements.txt
PORT=8032 python3 server.py
```

## Tests

```bash
python3 -m pip install pytest playwright -r requirements.txt
python3 -m unittest discover -s tests -p 'test_*.py'
```

Student records live in `classroom.sqlite3` (or the Docker data volume). Never commit them.
