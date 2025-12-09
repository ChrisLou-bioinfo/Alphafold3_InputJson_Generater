#!/bin/bash

# Ensure we are in the script's directory (workspace root)
cd "$(dirname "$0")"

echo "Starting AF3 Input Generator on port 19999..."
echo "Open http://127.0.0.1:19999 in your browser."

# Run the Flask app
python flask_tool/app.py
