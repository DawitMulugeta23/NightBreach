#!/bin/bash
echo "ROHA{chmod_unlocks_the_door}" > /home/player/locked_flag.txt
chown player:player /home/player/locked_flag.txt
chmod 000 /home/player/locked_flag.txt
