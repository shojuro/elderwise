# ElderWise APK Build Guide

## Overview
This guide provides multiple methods to build and test the ElderWise Android app.

## Method 1: PWA (Progressive Web App) - Quickest for Testing

### What You Get
- Installable web app that works like a native app
- Works on both Android and iOS
- No build tools required
- Can access camera for medication identification

### Steps
1. **Run the PWA server:**
   ```bash
   cd frontend/dist
   python3 serve.py
   ```

2. **On your phone:**
   - Connect to the same WiFi network as your computer
   - Find your computer's IP address:
     - Windows: `ipconfig`
     - Mac/Linux: `ifconfig` or `ip addr`
   - Open Chrome (Android) or Safari (iOS)
   - Navigate to: `http://YOUR_COMPUTER_IP:8080`
   - Android: Menu (3 dots) → "Add to Home screen"
   - iOS: Share button → "Add to Home Screen"

3. **Test the app:**
   - Open from your home screen
   - Grant camera permissions when prompted
   - Test medication identification feature

## Method 2: GitHub Actions - Automated Build

### Steps
1. **Push your code to GitHub:**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/ElderWise.git
   git push -u origin master
   ```

2. **Enable GitHub Actions:**
   - Go to your repository on GitHub
   - Click "Actions" tab
   - Enable workflows if prompted

3. **Trigger a build:**
   - Push any commit, or
   - Go to Actions → "Build Android APK" → "Run workflow"

4. **Download the APK:**
   - Once build completes, click the workflow run
   - Download "elderwise-debug-apk" artifact
   - Or check the Releases section

## Method 3: Local Build with Docker

### Create Docker Build Environment
Create `Dockerfile.android`:
```dockerfile
FROM openjdk:11-jdk

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
RUN apt-get install -y nodejs

# Install Android SDK
RUN apt-get update && apt-get install -y wget unzip
RUN wget https://dl.google.com/android/repository/commandlinetools-linux-8512546_latest.zip
RUN mkdir -p /android-sdk/cmdline-tools
RUN unzip commandlinetools-linux-8512546_latest.zip -d /android-sdk/cmdline-tools
RUN mv /android-sdk/cmdline-tools/cmdline-tools /android-sdk/cmdline-tools/latest

ENV ANDROID_HOME=/android-sdk
ENV PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools

# Accept licenses
RUN yes | sdkmanager --licenses
RUN sdkmanager "platform-tools" "platforms;android-33" "build-tools;33.0.0"

WORKDIR /app
```

### Build with Docker:
```bash
# Build Docker image
docker build -f Dockerfile.android -t elderwise-builder .

# Run build
docker run -v $(pwd):/app elderwise-builder bash -c "
  cd frontend &&
  npm install &&
  npm run build &&
  npx cap sync android &&
  cd android &&
  ./gradlew assembleDebug
"

# APK will be at: frontend/android/app/build/outputs/apk/debug/app-debug.apk
```

## Method 4: Local Build (Requires Setup)

### Prerequisites
1. **Install Node.js** (v16+)
2. **Install Java JDK 11**
   - Windows: Download from [adoptium.net](https://adoptium.net/)
   - Mac: `brew install openjdk@11`
   - Linux: `sudo apt install openjdk-11-jdk`

3. **Install Android SDK**
   - Easy way: Install [Android Studio](https://developer.android.com/studio)
   - Or use command line tools

4. **Set environment variables:**
   ```bash
   export ANDROID_HOME=$HOME/Android/Sdk  # Or your SDK path
   export PATH=$PATH:$ANDROID_HOME/platform-tools
   ```

### Build Steps
```bash
cd frontend

# Install dependencies
npm install

# Build React app
npm run build

# Sync with Capacitor
npx cap sync android

# Build APK
cd android
./gradlew assembleDebug

# Find APK at:
# android/app/build/outputs/apk/debug/app-debug.apk
```

## Method 5: Online Build Services

### 1. Capacitor Appflow
- Sign up at [ionic.io/appflow](https://ionic.io/appflow)
- Connect your GitHub repo
- Configure build settings
- Get APK from cloud builds

### 2. Expo EAS Build (if converting to Expo)
- Install Expo: `npm install -g eas-cli`
- Configure: `eas build:configure`
- Build: `eas build -p android`

## Testing the APK

### Install on Android Device
1. **Enable Developer Mode:**
   - Settings → About Phone
   - Tap "Build Number" 7 times

2. **Enable Unknown Sources:**
   - Settings → Security
   - Enable "Unknown Sources" or "Install unknown apps"

3. **Install APK:**
   - Transfer APK to phone (email, Google Drive, USB)
   - Open file manager
   - Tap the APK file
   - Follow installation prompts

### Test Key Features
1. **Camera Permission:**
   - Take photo of medication
   - Verify pill identification works

2. **PWA Features:**
   - Check offline functionality
   - Test app icon on home screen

3. **UI/UX:**
   - Verify large text for elderly users
   - Test navigation
   - Check accessibility features

## Troubleshooting

### Common Issues

1. **"npm install" fails:**
   ```bash
   rm -rf node_modules package-lock.json
   npm cache clean --force
   npm install
   ```

2. **Gradle build fails:**
   ```bash
   cd android
   ./gradlew clean
   ./gradlew assembleDebug --stacktrace
   ```

3. **Camera not working:**
   - Check AndroidManifest.xml has camera permissions
   - Ensure Capacitor Camera plugin is installed

4. **APK too large:**
   - Enable ProGuard in build.gradle
   - Use bundle format: `./gradlew bundleRelease`

## Quick Test Option

For immediate testing without building:
```bash
cd frontend
npm install
npm run dev  # Starts development server

# Access from phone browser at:
# http://YOUR_COMPUTER_IP:5173
```

## Production Build

For Google Play Store release:
1. Create signing key:
   ```bash
   keytool -genkey -v -keystore elderwise-key.keystore -alias elderwise -keyalg RSA -keysize 2048 -validity 10000
   ```

2. Configure signing in `android/app/build.gradle`

3. Build release APK:
   ```bash
   ./gradlew assembleRelease
   ```

## Need Help?

- Check the [Capacitor docs](https://capacitorjs.com/docs/android)
- Review [Android build docs](https://developer.android.com/studio/build)
- File issues on GitHub