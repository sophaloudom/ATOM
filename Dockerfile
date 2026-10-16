FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
COPY deploy/wheels /wheels
ARG OFFLINE_WHEELS=0
RUN if [ "$OFFLINE_WHEELS" = 1 ]; then pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt; else pip install --no-cache-dir -r requirements.txt; fi \
    && rm -rf /wheels && useradd --create-home atom
COPY --chown=atom:atom config ./config
COPY --chown=atom:atom hub ./hub
COPY --chown=atom:atom manage.py .
RUN mkdir -p /app/staticfiles && chown atom:atom /app/staticfiles
USER atom
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
