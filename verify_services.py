#!/usr/bin/env python3
"""
Service Verification Script for ElderWise
Checks if all required services are running and accessible
"""

import os
import sys
import redis
import pymongo
from pinecone import Pinecone
from dotenv import load_dotenv
import requests
from colorama import init, Fore, Style

# Initialize colorama for cross-platform colored output
init()

# Load environment variables
load_dotenv()

def print_status(service, status, message=""):
    """Print service status with color coding"""
    if status:
        print(f"{Fore.GREEN}✓{Style.RESET_ALL} {service}: {Fore.GREEN}OK{Style.RESET_ALL} {message}")
    else:
        print(f"{Fore.RED}✗{Style.RESET_ALL} {service}: {Fore.RED}FAILED{Style.RESET_ALL} {message}")

def check_env_vars():
    """Check if required environment variables are set"""
    print(f"\n{Fore.YELLOW}Checking Environment Variables...{Style.RESET_ALL}")
    
    required_vars = {
        "HF_TOKEN": "Hugging Face API Token",
        "PINECONE_API_KEY": "Pinecone API Key",
    }
    
    all_good = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value and value != f"your_{var.lower()}_here":
            print_status(description, True, "(configured)")
        else:
            print_status(description, False, "(not configured)")
            all_good = False
    
    return all_good

def check_redis():
    """Check Redis connectivity"""
    print(f"\n{Fore.YELLOW}Checking Redis...{Style.RESET_ALL}")
    
    try:
        r = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=int(os.getenv("REDIS_DB", 0)),
            password=os.getenv("REDIS_PASSWORD"),
            decode_responses=True
        )
        r.ping()
        print_status("Redis", True, f"Connected to {os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', 6379)}")
        return True
    except Exception as e:
        print_status("Redis", False, f"Error: {str(e)}")
        return False

def check_mongodb():
    """Check MongoDB connectivity"""
    print(f"\n{Fore.YELLOW}Checking MongoDB...{Style.RESET_ALL}")
    
    try:
        client = pymongo.MongoClient(
            os.getenv("MONGODB_URI", "mongodb://localhost:27017/"),
            serverSelectionTimeoutMS=5000
        )
        # Test connection
        client.server_info()
        db_name = os.getenv("MONGODB_DATABASE", "elderwise_ai")
        db = client[db_name]
        collections = db.list_collection_names()
        print_status("MongoDB", True, f"Connected to database '{db_name}' with {len(collections)} collections")
        client.close()
        return True
    except Exception as e:
        print_status("MongoDB", False, f"Error: {str(e)}")
        return False

def check_pinecone():
    """Check Pinecone connectivity"""
    print(f"\n{Fore.YELLOW}Checking Pinecone...{Style.RESET_ALL}")
    
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key or api_key == "your_pinecone_api_key_here":
        print_status("Pinecone", False, "API key not configured")
        return False
    
    try:
        pc = Pinecone(api_key=api_key)
        indexes = pc.list_indexes()
        index_name = os.getenv("PINECONE_INDEX_NAME", "elderwise-memory")
        
        # Check if our index exists
        index_exists = any(idx.name == index_name for idx in indexes)
        
        if index_exists:
            print_status("Pinecone", True, f"Index '{index_name}' exists")
        else:
            print_status("Pinecone", True, f"Connected, but index '{index_name}' does not exist")
            print(f"  {Fore.YELLOW}Available indexes: {', '.join([idx.name for idx in indexes]) or 'None'}{Style.RESET_ALL}")
        
        return True
    except Exception as e:
        print_status("Pinecone", False, f"Error: {str(e)}")
        return False

def check_huggingface():
    """Check Hugging Face API connectivity"""
    print(f"\n{Fore.YELLOW}Checking Hugging Face API...{Style.RESET_ALL}")
    
    token = os.getenv("HF_TOKEN")
    if not token or token == "your_hugging_face_token_here":
        print_status("Hugging Face API", False, "Token not configured")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            "https://huggingface.co/api/whoami",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            user_info = response.json()
            print_status("Hugging Face API", True, f"Authenticated as '{user_info.get('name', 'Unknown')}'")
            return True
        else:
            print_status("Hugging Face API", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        print_status("Hugging Face API", False, f"Error: {str(e)}")
        return False

def main():
    """Main verification routine"""
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}ElderWise Service Verification{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    
    # Track overall status
    all_services_ok = True
    
    # Check environment variables
    env_ok = check_env_vars()
    all_services_ok = all_services_ok and env_ok
    
    # Check services
    redis_ok = check_redis()
    mongodb_ok = check_mongodb()
    pinecone_ok = check_pinecone()
    hf_ok = check_huggingface()
    
    all_services_ok = all_services_ok and redis_ok and mongodb_ok and pinecone_ok and hf_ok
    
    # Summary
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    if all_services_ok:
        print(f"{Fore.GREEN}✓ All services are operational!{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}✗ Some services need attention.{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Next steps:{Style.RESET_ALL}")
        
        if not env_ok:
            print(f"1. Update the .env file with your API keys")
        
        if not redis_ok:
            print(f"2. Start Redis: {Fore.CYAN}redis-server{Style.RESET_ALL}")
        
        if not mongodb_ok:
            print(f"3. Start MongoDB: {Fore.CYAN}mongod{Style.RESET_ALL}")
        
        if not pinecone_ok and env_ok:
            print(f"4. Create Pinecone index '{os.getenv('PINECONE_INDEX_NAME', 'elderwise-memory')}'")
        
        if not hf_ok and env_ok:
            print(f"5. Verify your Hugging Face token has API access")
    
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    
    return 0 if all_services_ok else 1

if __name__ == "__main__":
    sys.exit(main())