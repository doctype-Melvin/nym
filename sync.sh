#!/bin/bash

SRC="/Users/webdev/Documents/Complyable/complyable-code"
DST="/Users/webdev/Documents/Complyable/complyable_app"

# UI python files
cp -f "$SRC/ui/"*.py "$DST/ui/"
echo "✅ Synced ui/*.py"

# Requirements and Dockerfile
cp -f "$SRC/requirements.txt" "$DST/requirements.txt"
cp -f "$SRC/Dockerfile" "$DST/Dockerfile"
echo "✅ Synced requirements.txt and Dockerfile"

echo "🎉 Sync complete"
