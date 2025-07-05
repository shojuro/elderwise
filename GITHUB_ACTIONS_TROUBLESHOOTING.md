# GitHub Actions APK Build Troubleshooting

## The Issue You Experienced

The workflow failed due to **deprecated GitHub Actions**. Here's what was wrong and how it's now fixed:

### Problems Fixed:
1. ✅ Updated `actions/upload-artifact@v3` → `v4`
2. ✅ Updated all actions to latest versions
3. ✅ Simplified the workflow to be more reliable
4. ✅ Added proper error handling
5. ✅ Used JDK 17 instead of 11 (better compatibility)

## New Simplified Workflow

The updated workflow (`build-apk.yml`) now:
- Uses only supported, non-deprecated actions
- Has better error handling
- Creates gradlew wrapper if missing
- Uploads APK artifacts that last 30 days
- Creates GitHub releases automatically

## Testing Your Setup

**Run this first to test basic setup:**
```
Actions → "Test Basic Build" → "Run workflow"
```

This will verify:
- Node.js setup works
- npm install works
- Project structure is correct
- Capacitor configuration is valid

## Quick Fix Steps

1. **Commit the fixed workflow:**
```bash
git add .github/workflows/
git commit -m "fix: Update GitHub Actions workflow with non-deprecated actions"
git push origin master
```

2. **Test the workflow:**
- Go to GitHub → Actions tab
- Click "Test Basic Build" → "Run workflow"
- If that works, try "Build Android APK"

## Common Issues and Solutions

### Issue: APK hangs on loading / white screen

**Symptoms:**
- App installs successfully but shows white screen
- "Loading..." message never disappears  
- App appears to hang indefinitely

**Causes:**
1. PWA service worker conflicts with APK WebView
2. Absolute paths in HTML don't resolve in APK context
3. Manifest.json PWA references cause WebView confusion

**Solution:**
```yaml
# Remove PWA artifacts before build
- name: Remove PWA artifacts
  run: |
    rm -f public/sw.js public/manifest.json
    sed -i '/<link rel="manifest"/d' index.html
    
# Fix absolute paths after build
- name: Fix paths
  run: |
    sed -i 's|href="/|href="./|g' dist/index.html
    sed -i 's|src="/|src="./|g' dist/index.html
```

**Use the "Build APK (Fixed)" workflow which includes all these fixes.**

### Issue: "Package conflicts with an existing package"

**Symptoms:**
- Installation fails with package conflict error
- Can't install debug and release versions side-by-side

**Causes:**
- Same package ID used for different builds
- Different signing keys for same package ID

**Solution:**
```yaml
# Use different package IDs for debug/release
Debug: com.elderwise.app.debug
Release: com.elderwise.app
```

**The fixed workflows now properly handle package IDs.**

### Issue: "npm ci" fails
**Solution:** The workflow now uses `npm ci || npm install` as fallback

### Issue: "gradlew not found"
**Solution:** The workflow now creates gradlew wrapper automatically

### Issue: "APK not found"
**Solution:** The workflow now searches for APK files and shows their location

### Issue: "Permissions denied"
**Solution:** Added proper permissions to the workflow

## What You'll Get

When the workflow succeeds:
1. **Artifact:** APK available in Actions tab for 30 days
2. **Release:** Automatic GitHub release with downloadable APK
3. **Clear instructions:** Download and install instructions included

## Specific Error: "Task 'assembleDebug' not found"

**This is the error you encountered!** 

**Problem:** The Android project structure isn't properly set up by Capacitor.

**Root Cause:** 
- The existing `android/` directory was incomplete
- Gradle couldn't find the `app` module
- `assembleDebug` task exists in the `app` subproject, not root

**Solution Applied:**
The updated workflow now:
1. ✅ **Removes old android directory:** `rm -rf android`
2. ✅ **Creates fresh Android project:** `npx cap add android`
3. ✅ **Uses correct build command:** `./gradlew app:assembleDebug`
4. ✅ **Verifies project structure** before building

## Try These Workflows

### Option 1: Main Workflow (Recommended)
```
Actions → "Build Android APK" → "Run workflow"
```

### Option 2: Simple Workflow (Backup)
```
Actions → "Build APK (Simple)" → "Run workflow"
```

The simple workflow is more basic but should definitely work.

## If It Still Fails

1. **Check the logs:** Look for specific error messages
2. **Try the simple workflow first:** It has fewer moving parts
3. **Manual trigger:** Use "Run workflow" button
4. **Check build outputs:** The workflow now shows detailed debugging info

**Most likely fix:** The updated workflow should work because it:
- Completely rebuilds the Android project from scratch
- Uses the correct Gradle task (`app:assembleDebug` instead of `assembleDebug`)
- Verifies each step before proceeding

The workflow is now much more robust and should handle this specific "assembleDebug not found" error.