#!/bin/bash
# Double-click to start the real-time IC Analyst watcher.
cd "$(dirname "$0")" || exit 1
python3 scripts/ic_watch.py
