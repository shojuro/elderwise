#!/bin/bash

# ElderWise APK Build Script

echo "============================================"
echo "ElderWise APK Builder"
echo "============================================"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check prerequisites
check_prerequisite() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}Error: $1 is not installed${NC}"
        echo "Please install $2"
        exit 1
    fi
}

# Check if we're in the frontend directory
if [ ! -f "package.json" ]; then
    echo -e "${RED}Error: This script must be run from the frontend directory${NC}"
    exit 1
fi

# Check for Java
check_prerequisite "java" "Java JDK 11 or higher"

# Check for Android SDK
if [ -z "$ANDROID_HOME" ]; then
    echo -e "${YELLOW}Warning: ANDROID_HOME is not set${NC}"
    echo "Trying common Android SDK locations..."
    
    # Common Android SDK locations
    if [ -d "$HOME/Android/Sdk" ]; then
        export ANDROID_HOME="$HOME/Android/Sdk"
    elif [ -d "/usr/local/android-sdk" ]; then
        export ANDROID_HOME="/usr/local/android-sdk"
    else
        echo -e "${RED}Error: Android SDK not found${NC}"
        echo "Please install Android Studio and set ANDROID_HOME"
        exit 1
    fi
fi

echo -e "${GREEN}✓ Android SDK found at: $ANDROID_HOME${NC}"

# Step 1: Clean previous builds
echo -e "\n${BLUE}Step 1: Cleaning previous builds...${NC}"
rm -rf dist
if [ -d "android" ]; then
    cd android
    ./gradlew clean
    cd ..
fi

# Step 2: Build the web app
echo -e "\n${BLUE}Step 2: Building web app...${NC}"
npm run build

# Step 3: Sync with Capacitor
echo -e "\n${BLUE}Step 3: Syncing with Capacitor...${NC}"
npx cap sync android

# Step 4: Update Android manifest for elder-friendly features
echo -e "\n${BLUE}Step 4: Updating Android configuration...${NC}"
if [ -d "android" ]; then
    # Create a custom AndroidManifest.xml with elder-friendly permissions
    cat > android/app/src/main/AndroidManifest.xml << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/AppTheme"
        android:usesCleartextTraffic="true"
        android:largeHeap="true"
        tools:targetApi="31">

        <activity
            android:configChanges="orientation|keyboardHidden|keyboard|screenSize|locale|smallestScreenSize|screenLayout|uiMode"
            android:name=".MainActivity"
            android:label="@string/title_activity_main"
            android:theme="@style/AppTheme.NoActionBarLaunch"
            android:launchMode="singleTask"
            android:exported="true"
            android:screenOrientation="portrait">

            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>

        </activity>

        <provider
            android:name="androidx.core.content.FileProvider"
            android:authorities="${applicationId}.fileprovider"
            android:exported="false"
            android:grantUriPermissions="true">
            <meta-data
                android:name="android.support.FILE_PROVIDER_PATHS"
                android:resource="@xml/file_paths"></meta-data>
        </provider>
    </application>

    <!-- Permissions -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.VIBRATE" />
    <uses-permission android:name="android.permission.WAKE_LOCK" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
    <uses-permission android:name="android.permission.RECORD_AUDIO" />
    <uses-permission android:name="android.permission.MODIFY_AUDIO_SETTINGS" />
    
    <!-- Features -->
    <uses-feature android:name="android.hardware.microphone" android:required="false" />
    
</manifest>
EOF
fi

# Step 5: Build the APK
echo -e "\n${BLUE}Step 5: Building APK...${NC}"
cd android

# Build debug APK
echo -e "${YELLOW}Building debug APK...${NC}"
./gradlew assembleDebug

# Check if build was successful
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✓ APK build successful!${NC}"
    
    # Find and display APK location
    APK_PATH="app/build/outputs/apk/debug/app-debug.apk"
    if [ -f "$APK_PATH" ]; then
        FULL_PATH="$(pwd)/$APK_PATH"
        echo -e "\n${GREEN}APK location:${NC}"
        echo "$FULL_PATH"
        
        # Get APK size
        APK_SIZE=$(du -h "$APK_PATH" | cut -f1)
        echo -e "\n${GREEN}APK size:${NC} $APK_SIZE"
        
        # Copy to frontend directory for easy access
        cp "$APK_PATH" ../elderwise-debug.apk
        echo -e "\n${GREEN}APK copied to:${NC}"
        echo "$(dirname $(pwd))/elderwise-debug.apk"
    fi
else
    echo -e "\n${RED}✗ APK build failed${NC}"
    echo "Check the error messages above"
    exit 1
fi

cd ..

echo -e "\n${YELLOW}To build a release APK:${NC}"
echo "1. Create a keystore: keytool -genkey -v -keystore elderwise.keystore -alias elderwise -keyalg RSA -keysize 2048 -validity 10000"
echo "2. Run: ./build-apk.sh --release"

echo -e "\n${YELLOW}To install on a connected device:${NC}"
echo "adb install elderwise-debug.apk"

echo "============================================"