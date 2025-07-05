#!/bin/bash

echo "============================================"
echo "ElderWise PWA Test Package Creator"
echo "============================================"

# Create a simple build directory
echo -e "\n\033[0;34mCreating PWA test package...\033[0m"

# Create dist directory if it doesn't exist
mkdir -p dist

# Copy the web-build files
cp -r web-build/* dist/ 2>/dev/null || {
    # If web-build doesn't exist, create a minimal version
    cat > dist/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="theme-color" content="#4a5568">
    <link rel="manifest" href="/manifest.json">
    <title>ElderWise</title>
    <style>
        body {
            margin: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            background: #f7fafc;
            padding: 20px;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2d3748;
            text-align: center;
            font-size: 2em;
            margin-bottom: 20px;
        }
        .install-btn {
            display: block;
            width: 100%;
            padding: 15px;
            background: #4299e1;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1.2em;
            cursor: pointer;
            margin: 20px 0;
        }
        .install-btn:hover {
            background: #3182ce;
        }
        .feature {
            padding: 15px;
            margin: 10px 0;
            background: #edf2f7;
            border-radius: 8px;
        }
        .feature h3 {
            margin: 0 0 10px 0;
            color: #2d3748;
        }
        .instructions {
            background: #e6fffa;
            border: 1px solid #81e6d9;
            border-radius: 8px;
            padding: 15px;
            margin: 20px 0;
        }
        .instructions h3 {
            color: #234e52;
            margin-top: 0;
        }
        .instructions ol {
            margin: 10px 0;
            padding-left: 20px;
        }
        .instructions li {
            margin: 5px 0;
        }
        .warning {
            background: #fed7d7;
            border: 1px solid #fc8181;
            border-radius: 8px;
            padding: 15px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏥 ElderWise</h1>
        <p style="text-align: center; color: #718096; font-size: 1.1em;">
            Your AI-Powered Elderly Care Companion
        </p>
        
        <button class="install-btn" id="installBtn" style="display: none;">
            📱 Install ElderWise App
        </button>
        
        <div class="instructions">
            <h3>📲 How to Test on Your Phone:</h3>
            <ol>
                <li><strong>On Android:</strong> Open Chrome browser</li>
                <li><strong>On iPhone:</strong> Open Safari browser</li>
                <li>Navigate to this URL on your phone</li>
                <li>For <strong>Android</strong>: Tap the menu (3 dots) → "Add to Home screen"</li>
                <li>For <strong>iPhone</strong>: Tap Share button → "Add to Home Screen"</li>
                <li>Give it a name and tap "Add"</li>
                <li>Open from your home screen to test!</li>
            </ol>
        </div>
        
        <div class="feature">
            <h3>💊 Medication Identification</h3>
            <p>Take a photo of any pill to instantly identify it and get detailed information.</p>
        </div>
        
        <div class="feature">
            <h3>🧠 Smart Memory Assistant</h3>
            <p>AI-powered memory support that learns and adapts to your needs.</p>
        </div>
        
        <div class="feature">
            <h3>❤️ Health Tracking</h3>
            <p>Monitor vital signs and get personalized health insights.</p>
        </div>
        
        <div class="feature">
            <h3>💬 Compassionate AI Companion</h3>
            <p>Always available to chat, answer questions, and provide support.</p>
        </div>
        
        <div class="warning">
            <strong>⚠️ Test Version:</strong> This is a test build for development. The full React app requires proper building with Node.js.
        </div>
    </div>
    
    <script>
        // PWA install prompt
        let deferredPrompt;
        const installBtn = document.getElementById('installBtn');
        
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            installBtn.style.display = 'block';
        });
        
        installBtn.addEventListener('click', async () => {
            if (deferredPrompt) {
                deferredPrompt.prompt();
                const { outcome } = await deferredPrompt.userChoice;
                console.log(`User response: ${outcome}`);
                deferredPrompt = null;
                installBtn.style.display = 'none';
            }
        });
        
        // Register service worker
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js');
        }
    </script>
</body>
</html>
EOF
}

# Ensure manifest.json exists
if [ ! -f dist/manifest.json ]; then
    cp public/manifest.json dist/ 2>/dev/null || echo '{}' > dist/manifest.json
fi

# Ensure service worker exists
if [ ! -f dist/sw.js ]; then
    cp public/sw.js dist/ 2>/dev/null || {
        cat > dist/sw.js << 'EOF'
self.addEventListener('install', event => {
    console.log('Service Worker installing.');
});

self.addEventListener('activate', event => {
    console.log('Service Worker activated.');
});

self.addEventListener('fetch', event => {
    event.respondWith(fetch(event.request));
});
EOF
    }
fi

# Create a simple server script
cat > dist/serve.py << 'EOF'
#!/usr/bin/env python3
import http.server
import socketserver
import os

PORT = 8080

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Service-Worker-Allowed', '/')
        super().end_headers()

os.chdir(os.path.dirname(os.path.abspath(__file__)))

with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
    print(f"Server running at http://localhost:{PORT}/")
    print(f"To test on your phone:")
    print(f"1. Make sure your phone is on the same network")
    print(f"2. Find your computer's IP address (ifconfig or ipconfig)")
    print(f"3. Navigate to http://YOUR_IP:{PORT} on your phone")
    print(f"4. Add to home screen for app-like experience")
    print("\nPress Ctrl+C to stop the server")
    httpd.serve_forever()
EOF

chmod +x dist/serve.py

# Create deployment package
echo -e "\n\033[0;34mCreating deployment package...\033[0m"
cd dist
zip -r ../elderwise-pwa-test.zip * > /dev/null 2>&1
cd ..

echo -e "\n\033[0;32m✓ PWA test package created!\033[0m"
echo -e "\n\033[1;33mTo test the PWA:\033[0m"
echo "1. Run: cd dist && python3 serve.py"
echo "2. Open http://localhost:8080 in your browser"
echo "3. Or access from your phone using your computer's IP address"
echo ""
echo -e "\033[1;33mDeployment package created:\033[0m elderwise-pwa-test.zip"
echo ""
echo -e "\033[0;34mFor a real Android APK, you'll need:\033[0m"
echo "- Java JDK 11+"
echo "- Android SDK"
echo "- Android Studio (recommended)"
echo ""
echo -e "\033[0;34mAlternatively, you can:\033[0m"
echo "1. Push your code to GitHub"
echo "2. Use GitHub Actions to build the APK"
echo "3. Or use online services like Capacitor Appflow"