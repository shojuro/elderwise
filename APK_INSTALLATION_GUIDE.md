# ElderWise APK Installation Guide

## APK Download Locations

### 🎯 For Testing (Debug Builds)
- **Package ID:** `com.elderwise.app.debug`
- **App Name:** "ElderWise Debug"
- **Can coexist:** ✅ Install alongside production version
- **Download:** Actions → "Build Debug APK" → Artifacts
- **Retention:** 14 days

### 🚀 For Production Use (Release Builds)
- **Package ID:** `com.elderwise.app`
- **App Name:** "ElderWise"
- **Replaces:** Previous production versions
- **Download:** Releases section OR Actions → "Build Release APK"
- **Retention:** 90 days

## Avoiding Package Conflicts

### The Problem
- Android won't install over existing apps with same package ID
- Different builds may have different signatures
- Error: "Package conflicts with an existing package"

### The Solution
1. **For Testing:** Use debug builds (different package ID)
2. **For Upgrading:** Uninstall old version first
3. **For Comparing:** Keep debug and release versions

## Installation Steps

### Step 1: Download APK

#### From GitHub Releases (Recommended)
1. Go to your repository page
2. Click **"Releases"** (right sidebar)
3. Find latest release
4. Download the APK file (4-6MB)

#### From GitHub Actions
1. Go to **"Actions"** tab
2. Click on successful workflow run
3. Scroll to **"Artifacts"** section
4. Download and unzip the artifact

### Step 2: Prepare Your Device

#### Enable Unknown Sources
**Android 8.0+ (API 26+):**
1. Settings → Apps & notifications
2. Special app access → Install unknown apps
3. Select your browser/file manager
4. Enable "Allow from this source"

**Older Android:**
1. Settings → Security
2. Enable "Unknown sources"

#### Remove Old Versions (If Needed)
1. Long-press ElderWise app icon
2. Select "Uninstall" or drag to trash
3. Confirm removal

### Step 3: Install APK

1. **Transfer APK to device:**
   - Email to yourself
   - Google Drive/Dropbox
   - USB transfer
   - Direct browser download

2. **Open APK file:**
   - Find in Downloads folder
   - Tap the `.apk` file

3. **Install:**
   - Tap "Install"
   - Wait for installation
   - Tap "Open" or "Done"

### Step 4: First Launch Setup

1. **Grant Permissions:**
   - 📷 **Camera**: For medication identification
   - 📂 **Storage**: For app data
   - 🔔 **Notifications**: For health reminders

2. **Test Features:**
   - Open medication screen
   - Take a test photo
   - Verify camera works

## Troubleshooting

### Installation Issues

#### "App not installed"
- **Cause:** Insufficient storage
- **Solution:** Free up 50MB+ space

#### "Installation blocked"
- **Cause:** Unknown sources disabled
- **Solution:** Enable in security settings

#### "Package conflicts"
- **Cause:** Existing version installed
- **Solutions:**
  1. Uninstall old version first
  2. Use debug build instead
  3. Clear app data before installing

### Runtime Issues

#### App crashes on startup
1. **Clear app cache:**
   - Settings → Apps → ElderWise
   - Storage → Clear Cache
2. **Reset app data:**
   - Storage → Clear Data (removes settings)
3. **Reinstall app**

#### Camera not working
1. **Check permissions:**
   - Settings → Apps → ElderWise → Permissions
   - Enable Camera permission
2. **Restart app**

#### Features not working
1. **Check internet connection** (for API features)
2. **Update Android WebView** (Play Store)
3. **Restart device**

## Version Information

### Debug Builds
```
Package: com.elderwise.app.debug
Name: ElderWise Debug
Icon: Has "DEBUG" overlay
Size: 4-6MB
Purpose: Testing alongside production
```

### Release Builds
```
Package: com.elderwise.app
Name: ElderWise
Icon: Standard app icon
Size: 4-6MB
Purpose: Production use
```

## APK Security

### What to Expect
- **Size:** 4-6MB (normal for React Native/Capacitor apps)
- **Permissions:** Camera, Storage, Internet, Notifications
- **Source:** Built from open source code
- **Signature:** Debug signed (not Play Store signed)

### Safety Notes
- Only install APKs from trusted sources
- Verify file size (should be 4-6MB)
- Check app permissions before granting

## Advanced Installation

### Using ADB (Developers)
```bash
# Enable USB Debugging on device
# Connect device to computer

# Install APK
adb install ElderWise-vX.X.X.apk

# If package conflicts:
adb uninstall com.elderwise.app
adb install ElderWise-vX.X.X.apk

# Install debug version alongside:
adb install ElderWise-Debug-XXX.apk
```

### Batch Installation Script
```bash
#!/bin/bash
echo "ElderWise APK Installer"
echo "======================="

# Check if ADB is available
if command -v adb &> /dev/null; then
    echo "Installing via ADB..."
    adb install *.apk
else
    echo "Please install manually:"
    echo "1. Transfer APK to device"
    echo "2. Enable Unknown Sources"
    echo "3. Install APK file"
fi
```

## Support

### Common Questions

**Q: Why is the APK so small (4-6MB)?**
A: Efficient build with tree-shaking and compression. External dependencies loaded as needed.

**Q: Can I install both debug and release versions?**
A: Yes! Debug version uses different package ID (com.elderwise.app.debug).

**Q: Will this update automatically?**
A: No, APK installations require manual updates. Consider using Play Store version when available.

**Q: Is it safe to install?**
A: Yes, built from open source code. However, it's not Play Store signed, so Android will warn you.

### Getting Help

- **Installation issues:** Check this guide's troubleshooting section
- **App bugs:** Report in GitHub issues
- **Feature requests:** Open GitHub discussion
- **Security concerns:** Contact repository maintainers

Your ElderWise APK should now install successfully! 🎉