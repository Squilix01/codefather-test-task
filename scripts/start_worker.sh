#!/bin/sh
set -e

wait_for_rabbitmq() {
  until python - <<'PY'
import socket
import sys

sock = socket.socket()
sock.settimeout(1)
try:
    try:
        code = sock.connect_ex(("rabbitmq", 5672))
    except OSError:
        code = 1
finally:
    sock.close()

sys.exit(0 if code == 0 else 1)
PY
  do
    echo "Очікування RabbitMQ"
    sleep 1
  done
}

wait_for_rabbitmq

exec poetry run taskiq worker app.tasks.broker:broker app.tasks.notifications
