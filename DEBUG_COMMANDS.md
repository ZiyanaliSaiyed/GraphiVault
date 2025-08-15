# GraphiVault Debug Commands

## Quick Debug Commands

### 1. Check Vault Status
```bash
python python_backend/main.py get_vault_status --vault-path ./test_vault
```

### 2. Unlock Vault (if needed)
```bash
python python_backend/main.py unlock --vault-path ./test_vault --password test123
```

### 3. Test Image Upload (CLI)
```bash
# First, create a test base64 image
echo "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==" > test_image_base64.txt

# Then upload it
python python_backend/main.py add_image --vault-path ./test_vault --file-contents "$(cat test_image_base64.txt)" --tags '["test", "debug"]'
```

### 4. List All Images
```bash
python python_backend/main.py get_all_images --vault-path ./test_vault
```

### 5. Search Images
```bash
python python_backend/main.py search_images --vault-path ./test_vault --query "test"
```

## Browser Console Debug

### Check Upload Process
```javascript
// In browser console, monitor upload
console.log('Starting upload test...');

// Check vault store state
console.log('Vault locked:', vaultStore.isVaultLocked);
console.log('Vault password:', vaultStore.vaultPassword ? 'SET' : 'NOT SET');

// Test file upload manually
const testFile = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
// Then drag and drop or use file input
```

## Native App Debug

### Tauri Console Output
Look for these log patterns:
```
🔧 Rust: add_image_from_frontend called with X tags
🔐 Rust: Password provided for image upload
📊 Rust: Python backend result: ...
```

### Python Backend Output
Look for these patterns:
```
🔄 Core Engine: Processing image upload: /tmp/...
✅ Core Engine: Image validation passed: ...
🔐 Core Engine: Encrypting to: ...
✅ Core Engine: Encryption complete, size: X bytes
💾 Core Engine: Storing image record in database
🎉 Core Engine: Image upload completed successfully: ...
```

## Common Issues & Solutions

### Issue: "Vault not initialized"
**Solution**: Ensure vault is unlocked before upload
```bash
python python_backend/main.py unlock --vault-path ./test_vault --password test123
```

### Issue: "Invalid base64 data"
**Solution**: Check file conversion in FileUpload.vue
- Verify readFileAsBase64 function
- Check file size limits
- Ensure proper base64 encoding

### Issue: "Image validation failed"
**Solution**: Check image format and PIL availability
```bash
pip install Pillow
```

### Issue: Database errors
**Solution**: Recreate database with correct schema
```bash
rm test_vault/database/vault.db
python python_backend/main.py initialize --vault-path ./test_vault --password test123
```

## Performance Monitoring

### File Size Limits
- Maximum: 50MB per file
- Recommended: < 10MB for optimal performance
- Thumbnail generation: Automatic for valid images

### Upload Speed
- Small files (< 1MB): < 2 seconds
- Medium files (1-10MB): 2-10 seconds  
- Large files (10-50MB): 10-30 seconds

## Security Verification

### Encryption Check
```bash
# Verify files are encrypted
ls -la test_vault/data/
file test_vault/data/*.enc
```

### Database Integrity
```bash
# Check database structure
sqlite3 test_vault/database/vault.db ".schema"
sqlite3 test_vault/database/vault.db "SELECT COUNT(*) FROM images;"
```