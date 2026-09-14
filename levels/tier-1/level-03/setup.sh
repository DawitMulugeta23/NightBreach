#!/bin/bash
{
  for i in $(seq 1 200); do
    echo "$(date -d "-$i minutes" '+%Y-%m-%d %H:%M:%S') INFO request_id=$i status=200"
  done
  echo "2026-01-01 00:00:00 FLAG ROHA{grep_finds_what_you_need}"
  for i in $(seq 201 400); do
    echo "$(date -d "-$i minutes" '+%Y-%m-%d %H:%M:%S') INFO request_id=$i status=200"
  done
} > /home/player/access.log
chown player:player /home/player/access.log
