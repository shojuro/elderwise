#!/bin/bash

echo "🔧 Committing APK fixes..."

# Add all the new workflow files
git add .github/workflows/build-apk-fixed.yml
git add .github/workflows/build-apk-debug-enhanced.yml  
git add .github/workflows/build-apk-troubleshoot.yml

# Add documentation updates
git add GITHUB_ACTIONS_TROUBLESHOOTING.md
git add APK_TESTING_GUIDE.md

# Add this script too
git add commit-apk-fixes.sh

# Show what will be committed
echo "📋 Files to be committed:"
git status --short

# Commit with detailed message
git commit -m "fix: Resolve APK hanging and package conflict issues

- Remove PWA artifacts that cause WebView hanging
- Fix absolute paths to relative for APK compatibility  
- Add separate debug/release workflows with proper package IDs
- Add WebView debugging and enhanced error detection
- Update troubleshooting documentation

Fixes:
- APK hanging on white screen (PWA service worker conflict)
- Package conflict errors (proper debug/release separation)
- Build failures (improved error handling)

New workflows:
- build-apk-fixed.yml: Main fixed workflow with build type selection
- build-apk-debug-enhanced.yml: Enhanced debugging and verification
- build-apk-troubleshoot.yml: Diagnostic build for troubleshooting"

echo "✅ Committed! Now run: git push origin master"