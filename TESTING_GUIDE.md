# GraphiVault Image Upload Testing Guide

## Pre-Testing Setup

1. **Ensure Vault is Unlocked**
   ```bash
   # Test vault unlock
   python python_backend/main.py unlock --vault-path ./test_vault --password test123
   ```

2. **Verify Test Images**
   - Prepare test images in common formats: JPG, PNG, GIF
   - Test with various sizes: small (< 1MB), medium (1-10MB), large (10-50MB)
   - Include one invalid file (non-image) to test validation

## Testing Scenarios

### 1. Basic Upload Test
- **Action**: Upload a single small JPG image
- **Expected**: Success message, image appears in vault
- **Verify**: Check database for new record

### 2. Multiple File Upload
- **Action**: Upload 3-5 images simultaneously
- **Expected**: All valid images processed, invalid ones skipped
- **Verify**: Correct count in vault statistics

### 3. Large File Test
- **Action**: Upload image close to 50MB limit
- **Expected**: Successful upload with progress indication
- **Verify**: File properly encrypted and stored

### 4. Format Validation Test
- **Action**: Upload unsupported file (e.g., .txt renamed to .jpg)
- **Expected**: Validation error, file rejected
- **Verify**: No database entry created

### 5. Session Management Test
- **Action**: Upload image, lock vault, try to upload again
- **Expected**: First upload succeeds, second fails with vault locked error
- **Verify**: Proper error handling

## Debug Commands

### Check Vault Status
```bash
python python_backend/main.py get_vault_status --vault-path ./test_vault
```

### List All Images
```bash
python python_backend/main.py get_all_images --vault-path ./test_vault
```

### Search Images
```bash
python python_backend/main.py search_images --vault-path ./test_vault --query "imported"
```

## Expected Log Output

### Successful Upload:
```
🔧 Rust: add_image_from_frontend called with 2 tags
🔐 Rust: Password provided for image upload
📊 Rust: Python backend result: Ok(PythonBackendResponse { success: true, ... })
```

### Failed Upload:
```
❌ Error processing file test.jpg: Vault not unlocked
```

## Troubleshooting

### Common Issues:
1. **"Vault not initialized"** - Run unlock command first
2. **"Invalid base64 data"** - Check file conversion process
3. **"Image validation failed"** - Verify file format and size
4. **"Failed to store in database"** - Check database permissions

### Debug Steps:
1. Check vault unlock status
2. Verify file format and size
3. Check available disk space
4. Review error logs for specific issues
5. Test with minimal image file first