#!/bin/bash

# Generate app icons for Android

echo "============================================"
echo "Generating App Icons for ElderWise"
echo "============================================"

# Create base icon using ImageMagick (if available) or create placeholder
generate_icon() {
    local size=$1
    local output=$2
    
    if command -v convert &> /dev/null; then
        # Create a simple icon with ImageMagick
        convert -size ${size}x${size} xc:'#B8A9E0' \
                -fill white -gravity center \
                -font Arial -pointsize $((size/3)) \
                -annotate +0+0 'EW' \
                -bordercolor '#9B87D3' -border 2 \
                "$output"
    else
        # Create a placeholder file if ImageMagick is not available
        echo "Creating placeholder icon at $output"
        touch "$output"
    fi
}

# Create icon directories if they don't exist
mkdir -p android/app/src/main/res/mipmap-mdpi
mkdir -p android/app/src/main/res/mipmap-hdpi
mkdir -p android/app/src/main/res/mipmap-xhdpi
mkdir -p android/app/src/main/res/mipmap-xxhdpi
mkdir -p android/app/src/main/res/mipmap-xxxhdpi

# Generate icons in different sizes
echo "Generating Android icons..."
generate_icon 48 "android/app/src/main/res/mipmap-mdpi/ic_launcher.png"
generate_icon 72 "android/app/src/main/res/mipmap-hdpi/ic_launcher.png"
generate_icon 96 "android/app/src/main/res/mipmap-xhdpi/ic_launcher.png"
generate_icon 144 "android/app/src/main/res/mipmap-xxhdpi/ic_launcher.png"
generate_icon 192 "android/app/src/main/res/mipmap-xxxhdpi/ic_launcher.png"

# Generate round icons
generate_icon 48 "android/app/src/main/res/mipmap-mdpi/ic_launcher_round.png"
generate_icon 72 "android/app/src/main/res/mipmap-hdpi/ic_launcher_round.png"
generate_icon 96 "android/app/src/main/res/mipmap-xhdpi/ic_launcher_round.png"
generate_icon 144 "android/app/src/main/res/mipmap-xxhdpi/ic_launcher_round.png"
generate_icon 192 "android/app/src/main/res/mipmap-xxxhdpi/ic_launcher_round.png"

echo "✓ Icon generation complete!"

# Create a simple SVG icon for the web app
cat > public/icon.svg << 'EOF'
<svg width="512" height="512" xmlns="http://www.w3.org/2000/svg">
  <rect width="512" height="512" rx="100" fill="#B8A9E0"/>
  <text x="256" y="320" font-family="Arial, sans-serif" font-size="200" font-weight="bold" text-anchor="middle" fill="white">EW</text>
</svg>
EOF

echo "✓ Web icon created!"