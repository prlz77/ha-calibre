ARG BUILD_FROM=ghcr.io/hassio-addons/base/amd64:14.3.1
FROM ubuntu:22.04

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        wget \
        xz-utils \
        python3 \
        python3-pip \
        jq \
        xdg-utils \
        xvfb \
        libegl1 \
        libopengl0 \
        libxcb-cursor0 \
        libxcb-icccm4 \
        libxcb-image0 \
        libxcb-keysyms1 \
        libxcb-randr0 \
        libxcb-render-util0 \
        libxcb-shape0 \
        libxcb-xinerama0 \
        libgl1-mesa-glx \
        libxkbcommon-x11-0 \
        calibre \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY app/requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r /app/requirements.txt

COPY app /app
COPY run.sh /

RUN chmod a+x /run.sh

EXPOSE 8080
WORKDIR /app

CMD [ "/run.sh" ]
