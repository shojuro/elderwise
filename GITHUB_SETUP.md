# GitHub Setup Guide for ElderWise APK Builds

This guide will walk you through setting up GitHub to automatically build APKs for ElderWise.

## Prerequisites

- A GitHub account
- Git installed on your local machine
- The ElderWise project code

## Step 1: Create a GitHub Repository

1. Go to [GitHub.com](https://github.com) and sign in
2. Click the **"+"** icon in the top right → **"New repository"**
3. Repository settings:
   - **Repository name**: `ElderWise`
   - **Description**: "AI-powered elderly care companion with medication identification"
   - **Visibility**: Choose Public or Private
   - **Do NOT** initialize with README, .gitignore, or license (we already have these)
4. Click **"Create repository"**

## Step 2: Connect Your Local Repository

After creating the repository, GitHub will show you commands. Use these in your terminal:

```bash
# Navigate to your project directory
cd /path/to/ElderWise

# Add the remote repository
git remote add origin https://github.com/YOUR_USERNAME/ElderWise.git

# Verify the remote was added
git remote -v
```

## Step 3: Initialize Android Project (Local)

Before pushing, ensure the Android project is properly initialized:

```bash
# Navigate to frontend directory
cd frontend

# Make the init script executable
chmod +x init-android.sh

# Run the initialization
./init-android.sh
```

This script will:
- Install dependencies
- Build the React app
- Initialize Capacitor Android project
- Create necessary Gradle files
- Generate package-lock.json

## Step 4: Commit and Push

```bash
# Go back to project root
cd ..

# Check status
git status

# Add the new/modified files
git add .github/workflows/build-apk.yml
git add frontend/init-android.sh
git add frontend/.gitignore
git add GITHUB_SETUP.md
git add BUILD_APK_GUIDE.md

# Commit
git commit -m "feat: Add GitHub Actions workflow for automated APK builds

- Add robust workflow that handles missing gradle wrapper
- Create initialization script for Android project
- Update documentation for GitHub setup
- Add proper .gitignore for frontend

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to GitHub
git push -u origin master
```

If you get an error about the branch name, try:
```bash
git push -u origin main
```

## Step 5: Enable GitHub Actions

1. Go to your repository on GitHub
2. Click the **"Actions"** tab
3. You should see "Build Android APK" workflow
4. If prompted to enable Actions, click **"I understand my workflows, go ahead and enable them"**

## Step 6: Trigger Your First Build

### Option A: Automatic (on push)
The workflow runs automatically when you push to master/main branch.

### Option B: Manual Trigger
1. Go to **Actions** tab
2. Click **"Build Android APK"** in the left sidebar
3. Click **"Run workflow"** button
4. Select branch (master/main)
5. Click **"Run workflow"**

## Step 7: Monitor the Build

1. Click on the running workflow to see progress
2. Each step will show ✓ when complete
3. The build typically takes 5-10 minutes

## Step 8: Download Your APK

### From Actions (Every Build)
1. Once the build completes successfully
2. Scroll down to **"Artifacts"** section
3. Download **"elderwise-debug-apk"**
4. Extract the ZIP file to get your APK

### From Releases (Push to Master Only)
1. Go to **"Releases"** section of your repository
2. Find the latest release (e.g., "ElderWise Build 1")
3. Download the APK file directly

## Troubleshooting

### Build Fails: "gradlew not found"
The workflow now handles this automatically, but if issues persist:
1. Run `./init-android.sh` locally
2. Commit and push the generated files

### Build Fails: "Could not find or load main class"
This happens if gradle wrapper is corrupted:
1. Delete `frontend/android/gradle` folder locally
2. Run `./init-android.sh` again
3. Commit and push

### Build Fails: "Package androidx.* does not exist"
1. Check `frontend/android/app/build.gradle` has correct dependencies
2. Ensure `capacitor.config.json` exists in frontend/

### Permission Denied Errors
The workflow now sets permissions automatically, but if you see errors:
```bash
cd frontend/android
chmod +x gradlew
git add gradlew
git commit -m "fix: Make gradlew executable"
git push
```

## Build Configuration

### Customizing the Build

Edit `.github/workflows/build-apk.yml` to:
- Change Node.js version (line 22)
- Change Java version (line 46)
- Modify build commands
- Add signing configuration for release builds

### Release Builds

For signed release APKs:
1. Generate a keystore
2. Add secrets to GitHub repository settings
3. Update workflow to use signing configuration

## GitHub Secrets (Optional)

For enhanced security, add secrets:
1. Go to Settings → Secrets and variables → Actions
2. Add secrets like:
   - `ANDROID_KEYSTORE` (base64 encoded keystore)
   - `KEYSTORE_PASSWORD`
   - `KEY_ALIAS`
   - `KEY_PASSWORD`

## Best Practices

1. **Branch Protection**: Set up branch protection rules for master/main
2. **PR Builds**: The workflow runs on pull requests too
3. **Version Tags**: Create tags for important releases
4. **Release Notes**: Edit releases to add detailed notes

## Getting Help

- Check the [Actions log](../../actions) for detailed error messages
- Review [Capacitor Android docs](https://capacitorjs.com/docs/android)
- File issues in your GitHub repository
- Check GitHub Actions [documentation](https://docs.github.com/actions)

## Next Steps

1. Install the APK on your Android device
2. Test all features, especially:
   - Camera for medication identification
   - Offline functionality
   - Performance on older devices
3. Gather feedback and iterate
4. Consider setting up:
   - Automated testing
   - Code signing for production
   - Google Play Store deployment

Happy building! 🚀