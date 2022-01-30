# Use retag of alpine:3.15 to force reproducible builds
FROM alanmpinder/upstream-alpine-3.15:c059bfaa849c

RUN apk add --no-cache python3 py3-pip && \
    pip3 install base64io pyyaml && \
    rm -rf /root/.cache

COPY app /app
WORKDIR /app

RUN chmod +x /app/main.py

ENTRYPOINT [ "/app/main.py" ]
