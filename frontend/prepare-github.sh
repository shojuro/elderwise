#!/bin/bash

echo "============================================"
echo "Preparing ElderWise for GitHub Actions"
echo "============================================"

# Create a minimal package-lock.json if it doesn't exist
if [ ! -f package-lock.json ]; then
    echo "Creating package-lock.json..."
    echo '{
  "name": "frontend",
  "version": "0.0.0",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "": {
      "name": "frontend",
      "version": "0.0.0",
      "dependencies": {},
      "devDependencies": {}
    }
  }
}' > package-lock.json
    echo "✓ Created minimal package-lock.json"
fi

# Create minimal dist directory for Capacitor
if [ ! -d dist ]; then
    echo "Creating dist directory..."
    mkdir -p dist
    echo '<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ElderWise</title>
</head>
<body>
    <h1>ElderWise</h1>
    <p>This is a placeholder. GitHub Actions will build the full app.</p>
</body>
</html>' > dist/index.html
    echo "✓ Created dist directory"
fi

echo ""
echo "✅ Ready for GitHub!"
echo ""
echo "Next steps:"
echo "1. Commit all changes"
echo "2. Push to GitHub" 
echo "3. GitHub Actions will handle the full build"