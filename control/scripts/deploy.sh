#!/bin/bash
# Exclude the __pycache__ folder while syncing
rsync -avz --exclude '__pycache__' --exclude 'node_modules' -e ssh ./ pi@raspberrypi.local:~/app
