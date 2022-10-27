FROM python:3.10-slim-bullseye
LABEL description="eigenHelper container"
LABEL maintainer="Adam Sciegaj @adsci"
EXPOSE 5006
WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
ENV PYTHONPATH "/"

COPY eigenHelper/ ./eigenHelper/
ENTRYPOINT ["bokeh", "serve"]
CMD ["eigenHelper", "--allow-websocket-origin=*"]