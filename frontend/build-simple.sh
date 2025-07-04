#!/bin/bash

# Simple APK build script for ElderWise
# This script builds a basic APK without advanced mobile features

echo "============================================"
echo "ElderWise Simple APK Builder"
echo "============================================"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in the frontend directory
if [ ! -f "package.json" ]; then
    echo -e "${RED}Error: This script must be run from the frontend directory${NC}"
    exit 1
fi

# Step 1: Create a minimal dist directory with static files
echo -e "\n${BLUE}Step 1: Creating minimal web build...${NC}"
mkdir -p dist
cp -r public/* dist/ 2>/dev/null || true

# Create a minimal index.html
cat > dist/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ElderWise</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #B8A9E0 0%, #9B87D3 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 400px;
        }
        h1 {
            color: #6B46C1;
            margin-bottom: 20px;
            font-size: 2.5em;
        }
        p {
            color: #666;
            font-size: 1.2em;
            line-height: 1.6;
        }
        .logo {
            font-size: 4em;
            margin-bottom: 20px;
        }
        .coming-soon {
            background: #6B46C1;
            color: white;
            padding: 15px 30px;
            border-radius: 10px;
            font-weight: bold;
            margin-top: 30px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🤖</div>
        <h1>ElderWise</h1>
        <p>Your AI Memory Companion</p>
        <div class="coming-soon">
            Full App Coming Soon
        </div>
    </div>
</body>
</html>
EOF

echo -e "${GREEN}✓ Minimal web build created${NC}"

# Step 2: Initialize Capacitor manually
echo -e "\n${BLUE}Step 2: Setting up Capacitor configuration...${NC}"

# Create capacitor.config.json if it doesn't exist
if [ ! -f "capacitor.config.json" ]; then
    cat > capacitor.config.json << 'EOF'
{
  "appId": "com.elderwise.app",
  "appName": "ElderWise",
  "webDir": "dist",
  "bundledWebRuntime": false,
  "android": {
    "minSdkVersion": 23,
    "targetSdkVersion": 33,
    "compileSdkVersion": 34,
    "buildToolsVersion": "34.0.0"
  }
}
EOF
fi

# Step 3: Create Android project structure manually
echo -e "\n${BLUE}Step 3: Creating Android project structure...${NC}"

if [ ! -d "android" ]; then
    mkdir -p android/app/src/main/java/com/elderwise/app
    mkdir -p android/app/src/main/res/values
    mkdir -p android/app/src/main/res/mipmap-hdpi
    mkdir -p android/app/src/main/res/mipmap-mdpi
    mkdir -p android/app/src/main/res/mipmap-xhdpi
    mkdir -p android/app/src/main/res/mipmap-xxhdpi
    mkdir -p android/app/src/main/res/mipmap-xxxhdpi
    mkdir -p android/app/src/main/assets/public
fi

# Copy web assets
cp -r dist/* android/app/src/main/assets/public/

# Create basic MainActivity
cat > android/app/src/main/java/com/elderwise/app/MainActivity.java << 'EOF'
package com.elderwise.app;

import android.os.Bundle;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        WebView webView = findViewById(R.id.webview);
        webView.setWebViewClient(new WebViewClient());
        webView.getSettings().setJavaScriptEnabled(true);
        webView.getSettings().setDomStorageEnabled(true);
        webView.loadUrl("file:///android_asset/public/index.html");
    }
}
EOF

# Create layout
mkdir -p android/app/src/main/res/layout
cat > android/app/src/main/res/layout/activity_main.xml << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <WebView
        android:id="@+id/webview"
        android:layout_width="match_parent"
        android:layout_height="match_parent" />

</LinearLayout>
EOF

# Create strings.xml
cat > android/app/src/main/res/values/strings.xml << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">ElderWise</string>
    <string name="title_activity_main">ElderWise</string>
</resources>
EOF

# Create AndroidManifest.xml
cat > android/app/src/main/AndroidManifest.xml << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.elderwise.app">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:theme="@style/AppTheme">
        
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:label="@string/title_activity_main">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
EOF

# Create basic styles
cat > android/app/src/main/res/values/styles.xml << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="AppTheme" parent="Theme.AppCompat.Light.NoActionBar">
        <item name="colorPrimary">#B8A9E0</item>
        <item name="colorPrimaryDark">#9B87D3</item>
        <item name="colorAccent">#6B46C1</item>
    </style>
</resources>
EOF

# Create basic build.gradle
cat > android/app/build.gradle << 'EOF'
apply plugin: 'com.android.application'

android {
    compileSdkVersion 34
    buildToolsVersion "34.0.0"
    
    defaultConfig {
        applicationId "com.elderwise.app"
        minSdkVersion 23
        targetSdkVersion 33
        versionCode 1
        versionName "1.0"
    }
    
    buildTypes {
        release {
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
}

dependencies {
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
}
EOF

# Create project-level build.gradle
cat > android/build.gradle << 'EOF'
buildscript {
    repositories {
        google()
        jcenter()
    }
    dependencies {
        classpath 'com.android.tools.build:gradle:7.4.2'
    }
}

allprojects {
    repositories {
        google()
        jcenter()
    }
}

task clean(type: Delete) {
    delete rootProject.buildDir
}
EOF

# Create gradle.properties
cat > android/gradle.properties << 'EOF'
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
android.enableJetifier=true
EOF

# Create basic proguard file
touch android/app/proguard-rules.pro

# Create gradle wrapper
mkdir -p android/gradle/wrapper
cat > android/gradle/wrapper/gradle-wrapper.properties << 'EOF'
distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\://services.gradle.org/distributions/gradle-7.5-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
EOF

echo -e "${GREEN}✓ Android project structure created${NC}"

echo -e "\n${YELLOW}Simple APK build setup complete!${NC}"
echo -e "\n${BLUE}To build the APK:${NC}"
echo "1. Make sure you have Android SDK installed"
echo "2. Set ANDROID_HOME environment variable"
echo "3. Run: cd android && ./gradlew assembleDebug"
echo ""
echo -e "${YELLOW}Note: This creates a basic WebView-based APK${NC}"
echo "For full native features, complete the Capacitor setup first."