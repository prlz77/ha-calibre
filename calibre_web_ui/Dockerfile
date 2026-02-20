ARG BUILD_FROM
FROM ${BUILD_FROM}

ENV DEBIAN_FRONTEND=noninteractive

# Install Calibre CLI tools and dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        calibre \
        python3 \
        python3-pip \
        xvfb \
        xauth \
        jq \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY app/requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir --break-system-packages -r /app/requirements.txt

# Copy application files
COPY app /app
COPY run.sh /

RUN chmod a+x /run.sh

# Labels for Home Assistant
LABEL \
    io.hass.name="Calibre Web UI" \
    io.hass.description="A lightweight web interface for Calibre book management" \
    io.hass.type="addon" \
    io.hass.version="1.4.0"

EXPOSE 8080
WORKDIR /app

CMD [ "/run.sh" ]
