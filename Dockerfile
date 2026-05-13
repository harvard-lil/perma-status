FROM python:3.13-alpine

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    FLASK_APP=monitor.py

WORKDIR /app

RUN apk upgrade --no-cache

COPY requirements.txt .

RUN python -m pip install --upgrade "pip>=26.1" \
    && pip install --upgrade --no-cache-dir -r requirements.txt \
    && pip install --upgrade --no-cache-dir gunicorn

COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8080

ENTRYPOINT ["/entrypoint.sh"]

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "monitor:app"]
