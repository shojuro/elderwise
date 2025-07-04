#!/usr/bin/env python
"""
Test script to verify ElderWise AI setup
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_setup():
    print("🔍 Testing ElderWise AI Setup...")
    
    # Test 1: Environment Variables
    print("\n1. Checking environment variables...")
    required_vars = ["HF_TOKEN", "PINECONE_API_KEY", "MONGODB_URI"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"   ❌ Missing environment variables: {', '.join(missing_vars)}")
        print("   Please copy .env.example to .env and fill in the values")
        return
    else:
        print("   ✅ All required environment variables present")
    
    # Test 2: Import modules
    print("\n2. Testing module imports...")
    try:
        from src.config.settings import settings
        from src.memory.controller import MemoryController
        from src.utils.inference import mistral_inference
        print("   ✅ All modules imported successfully")
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        return
    
    # Test 3: Database connections
    print("\n3. Testing database connections...")
    try:
        from src.utils.database import redis_manager, mongodb_manager, pinecone_manager
        
        # Test Redis
        try:
            redis_manager.connect()
            redis_manager.get_client().ping()
            print("   ✅ Redis connection successful")
        except Exception as e:
            print(f"   ❌ Redis connection failed: {e}")
        
        # Test MongoDB
        try:
            await mongodb_manager.connect()
            await mongodb_manager.client.admin.command('ping')
            print("   ✅ MongoDB connection successful")
        except Exception as e:
            print(f"   ❌ MongoDB connection failed: {e}")
        
        # Test Pinecone
        try:
            pinecone_manager.connect()
            pinecone_manager.get_index().describe_index_stats()
            print("   ✅ Pinecone connection successful")
        except Exception as e:
            print(f"   ❌ Pinecone connection failed: {e}")
    
    except Exception as e:
        print(f"   ❌ Database test error: {e}")
    
    # Test 4: HuggingFace Token
    print("\n4. Testing Hugging Face token...")
    try:
        if mistral_inference.validate_token():
            print("   ✅ Hugging Face token is valid")
        else:
            print("   ❌ Hugging Face token validation failed")
    except Exception as e:
        print(f"   ❌ Token test error: {e}")
    
    print("\n✨ Setup test complete!")
    print("\nTo start the application, run:")
    print("  python run.py")
    print("\nOr for development:")
    print("  python -m uvicorn src.api.main:app --reload")

if __name__ == "__main__":
    asyncio.run(test_setup())