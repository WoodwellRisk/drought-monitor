#!/bin/bash
echo "Cleaning old build artifacts..."
rm -rf out
rm -rf src/drought_map/www/*

echo "=== Starting Build Process ==="
echo "Working directory: $(pwd)"

echo "Building Next.js app..."
npm install
npm run build

echo "Copying build output to Python package..."
cp -r out/* src/drought_map/www/


echo "Renaming files..."
MAIN_JS=$(find src/drought_map/www/_next/static/chunks -name "main-*.js" -type f | head -n 1)
if [ ! -z "$MAIN_JS" ]; then
    echo "Found JS: $MAIN_JS"
    mv "$MAIN_JS" src/drought_map/www/main.js
else
    echo "ERROR: Could not find main JS bundle!"
    exit 1
fi

MAIN_CSS=$(find src/drought_map/www/_next/static/css -name "*.css" -type f | head -n 1)
if [ ! -z "$MAIN_CSS" ]; then
    echo "Found CSS: $MAIN_CSS"
    mv "$MAIN_CSS" src/drought_map/www/styles.css
else
    echo "ERROR: Could not find main CSS file!"
    # Debug: Show what IS in the css folder
    ls -la src/drought_map/www/_next/static/css/
    exit 1
fi

echo "Build complete. Assets ready in src/drought_map/www/"