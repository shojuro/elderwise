#!/usr/bin/env python3
"""
Run medication-specific tests for ElderWise
"""
import subprocess
import sys
import os

def run_tests():
    """Run all medication-related tests"""
    test_commands = [
        # Backend medication service tests
        ["pytest", "tests/test_medication_services.py", "-v", "--tb=short"],
        
        # Backend medication API tests
        ["pytest", "tests/test_medication_api.py", "-v", "--tb=short"],
        
        # Frontend medication component tests
        ["npm", "test", "src/__tests__/MedicationScreen.test.tsx"],
    ]
    
    print("🧪 Running ElderWise Medication Tests")
    print("=" * 50)
    
    all_passed = True
    
    for i, cmd in enumerate(test_commands, 1):
        test_name = " ".join(cmd)
        print(f"\n[{i}/{len(test_commands)}] Running: {test_name}")
        print("-" * 50)
        
        try:
            if cmd[0] == "npm":
                # Change to frontend directory for npm tests
                result = subprocess.run(
                    cmd,
                    cwd="frontend",
                    capture_output=True,
                    text=True
                )
            else:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True
                )
            
            if result.returncode == 0:
                print("✅ PASSED")
                if result.stdout:
                    print(result.stdout)
            else:
                print("❌ FAILED")
                all_passed = False
                if result.stdout:
                    print(result.stdout)
                if result.stderr:
                    print("STDERR:", result.stderr)
                    
        except Exception as e:
            print(f"❌ ERROR running test: {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All medication tests passed!")
        return 0
    else:
        print("❌ Some tests failed. Please check the output above.")
        return 1


def check_dependencies():
    """Check if required dependencies are installed"""
    print("Checking dependencies...")
    
    # Check Python dependencies
    try:
        import pytest
        import aiohttp
        import PIL
        from google.cloud import vision
        print("✅ Python dependencies OK")
    except ImportError as e:
        print(f"❌ Missing Python dependency: {e}")
        print("Run: pip install -r requirements.txt")
        return False
    
    # Check if frontend dependencies are installed
    if not os.path.exists("frontend/node_modules"):
        print("❌ Frontend dependencies not installed")
        print("Run: cd frontend && npm install")
        return False
    
    print("✅ All dependencies OK")
    return True


if __name__ == "__main__":
    print("ElderWise Medication Test Suite")
    print("==============================")
    
    if not check_dependencies():
        sys.exit(1)
    
    exit_code = run_tests()
    sys.exit(exit_code)