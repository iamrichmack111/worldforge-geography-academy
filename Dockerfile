FROM python:3.12-slim
WORKDIR /app
COPY . /app
ENV PYTHONUNBUFFERED=1 PORT=8081 WORLDFORGE_HOST=0.0.0.0 WORLDFORGE_DB=/data/classroom.sqlite3
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /data && useradd -u 10001 -m worldforge && chown -R worldforge:worldforge /app /data
USER worldforge
EXPOSE 8081
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8081/classroom.html',timeout=3)" || exit 1
CMD ["python", "server.py"]
