#!/bin/bash
# Double-click to import a pro forma into the IC Go/No-Go dashboard.
# Or drag a spreadsheet onto this icon to import that file directly.
cd "$(dirname "$0")/.." || exit 1
python3 -m deal_agent.ic.desktop "$@"
