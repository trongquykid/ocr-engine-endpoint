#!/bin/bash

# Tên container cần ghi log
CONTAINER_NAME="ocr-engine-endpoint"

# File log lưu lại
LOG_FILE="app/logs/docker_request.log"

# Tạo log mới (nếu muốn giữ lại cũ, thì bỏ dòng này)
echo "=== Logging from container: $CONTAINER_NAME ===" > "$LOG_FILE"

# Kiểm tra container có tồn tại không
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  echo "Logging started for $CONTAINER_NAME"
  docker logs -f "$CONTAINER_NAME" >> "$LOG_FILE" 2>&1
else
  echo "Container $CONTAINER_NAME not found!"
  exit 1
fi
