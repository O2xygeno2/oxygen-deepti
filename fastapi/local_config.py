# local_config.py - For local development
import os

# For local development, use public IP with SSL
os.environ["DB_HOST"] = "34.100.220.171"
os.environ["DB_SSL"] = "require"  # Force SSL for public connection

# Test connection locally
async def test_local_connection():
    from database import test_connection
    if await test_connection():
        print("✅ Local connection successful")
    else:
        print("❌ Local connection failed")
