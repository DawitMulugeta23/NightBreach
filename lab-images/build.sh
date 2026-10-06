#!/bin/sh
# Builds the trusted NightBreach lab images with pinned version tags.
set -eu
cd "$(dirname "$0")"
docker build -t nightbreach/attacker:1.0 attacker
docker build -t nightbreach/linux-permissions-target:1.0 linux-permissions
