#!/bin/bash

# Function to handle Ctrl-C (SIGINT)
cleanup() {
    echo "Stopping Docker containers..."
    podman-compose down
    echo "Docker containers stopped."
    exit 0
}

# Build the ftdc_decoder binary
if [[ ! -f ./ftdc_decoder ]]; then
  CGO_ENABLED=1 \
  CGO_CFLAGS="" \
  CGO_CPPFLAGS="" \
  CGO_CXXFLAGS="" \
  CGO_LDFLAGS="" \
  GOOS=linux \
  GOARCH=amd64 \
  GOAMD64=v1 \
  go build -buildmode=exe -compiler=gc -o ./ftdc_decoder
fi

if [[ ! -f ./ftdc_decoder ]]; then
  echo ftdc_decoder binary not exists
  exit 1
fi

# Trap Ctrl-C (SIGINT) to run the cleanup function
trap cleanup SIGINT

# Start Docker containers in detached mode
podman-compose up -d

# Tail the logs of the metrics-processor service
podman-compose logs -f metrics-processor
