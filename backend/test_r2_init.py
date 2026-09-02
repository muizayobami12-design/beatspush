"""Quick test to verify R2 storage service initialization"""
from app.services.r2_storage_service import R2StorageService

# Initialize service
storage_service = R2StorageService()

print("=" * 60)
print("R2 STORAGE SERVICE TEST")
print("=" * 60)
print(f"Storage Type: {'R2' if storage_service.use_r2 else 'Local (Fallback)'}")
print(f"R2 Configured: {storage_service.use_r2}")
print("")

if storage_service.use_r2:
    print("✅ R2 is configured and ready!")
    print("   Files will be uploaded to Cloudflare R2 buckets")
else:
    print("✅ Local storage active (R2 not configured)")
    print("   Files will be saved to backend/uploads/")
    print("   To enable R2: Follow R2_SETUP_GUIDE.md")

print("=" * 60)
print("Service initialized successfully!")
print("=" * 60)
