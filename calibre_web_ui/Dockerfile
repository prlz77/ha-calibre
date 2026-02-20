ARG BUILD_FROM
FROM ${BUILD_FROM}

# Install Calibre CLI tools and Python/pip on Alpine
RUN apk add --no-cache \
        calibre \
        python3 \
        py3-pip \
        xvfb \
        jq

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
    io.hass.version="1.2.1"

EXPOSE 8080
WORKDIR /app

CMD [ "/run.sh" ]
