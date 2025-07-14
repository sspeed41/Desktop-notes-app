#!/usr/bin/env python3
"""
Standalone test script to diagnose Supabase storage upload issues
"""

import os
import sys
from datetime import datetime
from supabase import create_client

# Load environment variables
try:
    # Try to load from .streamlit/secrets.toml if running locally
    import toml
    with open('.streamlit/secrets.toml', 'r') as f:
        secrets = toml.load(f)
    
    SUPABASE_URL = secrets.get('SUPABASE_URL')
    SUPABASE_ANON_KEY = secrets.get('SUPABASE_ANON_KEY')
    SUPABASE_SERVICE_ROLE = secrets.get('SUPABASE_SERVICE_ROLE')
except:
    # Fallback to environment variables
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')
    SUPABASE_SERVICE_ROLE = os.getenv('SUPABASE_SERVICE_ROLE')

print("🔍 SUPABASE STORAGE DIAGNOSTIC TEST")
print("=" * 50)

# Test 1: Check configuration
print("\n1. Configuration Check:")
print(f"   SUPABASE_URL: {'✅ Set' if SUPABASE_URL else '❌ Missing'}")
print(f"   SUPABASE_ANON_KEY: {'✅ Set' if SUPABASE_ANON_KEY else '❌ Missing'}")
print(f"   SUPABASE_SERVICE_ROLE: {'✅ Set' if SUPABASE_SERVICE_ROLE else '❌ Missing'}")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    print("❌ Missing required configuration!")
    sys.exit(1)

# Test 2: Create clients
print("\n2. Client Creation:")
try:
    anon_client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    print("   ✅ Anonymous client created")
except Exception as e:
    print(f"   ❌ Anonymous client failed: {e}")
    sys.exit(1)

service_client = None
if SUPABASE_SERVICE_ROLE:
    try:
        service_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE)
        print("   ✅ Service role client created")
    except Exception as e:
        print(f"   ❌ Service role client failed: {e}")

# Test 3: List buckets
print("\n3. Bucket Access:")
try:
    buckets = anon_client.storage.list_buckets()
    bucket_names = [b.name for b in buckets] if buckets else []
    print(f"   Available buckets: {bucket_names}")
    
    if 'racing-notes-media' in bucket_names:
        print("   ✅ racing-notes-media bucket found")
    else:
        print("   ❌ racing-notes-media bucket NOT found")
        if bucket_names:
            print(f"   Available buckets: {bucket_names}")
        else:
            print("   No buckets accessible")
except Exception as e:
    print(f"   ❌ Bucket listing failed: {e}")

# Test 4: Create test file
print("\n4. Test File Upload:")
test_content = f"Test upload at {datetime.now()}"
test_filename = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
test_path = f"uploads/{test_filename}"

print(f"   Test file: {test_path}")
print(f"   Content: {test_content}")

# Test with anonymous client
print("\n   Testing with ANONYMOUS client:")
try:
    response = anon_client.storage.from_("racing-notes-media").upload(
        path=test_path,
        file=test_content.encode('utf-8'),
        file_options={"content-type": "text/plain"}
    )
    
    print(f"   Response type: {type(response)}")
    print(f"   Response: {response}")
    
    # Check for error
    error = getattr(response, 'error', None)
    if error:
        print(f"   ❌ Upload error: {error}")
    else:
        print("   ✅ Upload appears successful")
        
        # Try to get public URL
        try:
            public_url = anon_client.storage.from_("racing-notes-media").get_public_url(test_path)
            print(f"   ✅ Public URL: {public_url}")
        except Exception as url_e:
            print(f"   ❌ Public URL failed: {url_e}")
            
except Exception as e:
    print(f"   ❌ Anonymous upload failed: {e}")

# Test with service role client if available
if service_client:
    print("\n   Testing with SERVICE ROLE client:")
    try:
        response = service_client.storage.from_("racing-notes-media").upload(
            path=f"service_{test_path}",
            file=test_content.encode('utf-8'),
            file_options={"content-type": "text/plain"}
        )
        
        print(f"   Response type: {type(response)}")
        print(f"   Response: {response}")
        
        # Check for error
        error = getattr(response, 'error', None)
        if error:
            print(f"   ❌ Service upload error: {error}")
        else:
            print("   ✅ Service upload appears successful")
            
    except Exception as e:
        print(f"   ❌ Service upload failed: {e}")

print("\n" + "=" * 50)
print("🏁 DIAGNOSTIC COMPLETE")
print("\nIf uploads are failing, the output above should show the exact error.")
print("Common issues:")
print("- Bucket doesn't exist")
print("- Missing storage policies")
print("- Authentication issues")
print("- Network connectivity problems") 