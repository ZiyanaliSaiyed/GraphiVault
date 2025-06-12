# GraphiVault Python Backend

This directory contains the Python backend components for GraphiVault, organized into logical modules for better maintainability.

## Directory Structure

### 📁 core/
Core application functionality and business logic:
- `core_engine.py` - Main application engine
- `session_manager.py` - User session management
- `vault_manager.py` - Vault lifecycle management

### 🔐 crypto/
Cryptographic operations and security:
- `crypto_controller.py` - Main cryptography controller
- `encrypt.py` - File encryption utilities
- `decrypt.py` - File decryption utilities

### 🗄️ database/
Database operations and search functionality:
- `database_init.py` - Database initialization and schema
- `search_engine.py` - Image search and indexing

### 💾 storage/
File storage and management:
- `storage_interface.py` - Storage abstraction layer

### 🖼️ ui/
User interface and image processing:
- `image_processor.py` - Image processing and analysis
- `thumbnail.py` - Thumbnail generation

### 🔗 ipc/
Inter-process communication with Tauri frontend:
- `ipc_gateway.py` - Main IPC gateway (current)
- `ipc_gateway_new.py` - New IPC implementation
- `ipc_gateway_old.py` - Legacy IPC implementation

### 🧪 tests/
Test files and utilities:
- `test_backend.py` - Backend functionality tests
- `test_database_integration.py` - Database integration tests
- `simple_test.py` - Simple functionality tests

### 🛠️ utils/
Utility modules and helpers:
- `audit_logger.py` - Security and audit logging
- `tag_manager.py` - Image tagging and metadata

### 📄 Root Files
- `main.py` - Main entry point for the Python backend
- `config.json` - Configuration settings
- `__init__.py` - Package initialization

## Usage

The main entry point is `main.py` in the root directory. All modules are now properly organized and can be imported using their new paths:

```python
from core.vault_manager import VaultManager
from crypto.encrypt import encrypt_file
from database.search_engine import SearchEngine
# etc.
```

## Migration Notes

If you have existing imports in your code, you'll need to update them to reflect the new structure. The functionality remains the same, only the organization has changed.
