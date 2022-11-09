FROM python:3.10-slim-bullseye
LABEL description="eigenHelper container"
LABEL maintainer="Adam Sciegaj @adsci"
EXPOSE 5006
WORKDIR /app

RUN apt update && apt install -y curl

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
ENV PYTHONPATH "/"

COPY eigenHelper/ ./eigenHelper/
#Import only core calfem functions to reduce the image size
RUN curl -LJO https://raw.githubusercontent.com/CALFEM/calfem-python/master/calfem/core.py
RUN cp core.py ./eigenHelper/calfem/

ENTRYPOINT ["bokeh", "serve"]
CMD ["eigenHelper", "--allow-websocket-origin=*"]