# GraphiVault - Project Structure Documentation

This document outlines the organization and structure of the GraphiVault project.

## Top-Level Directories

- **src/** - Vue 3 frontend code
- **src-tauri/** - Rust-based Tauri application code
- **python_backend/** - Python backend services
- **test_vault/** - Test environment for development

## Frontend Structure (src/)

- **components/** - Reusable Vue components
  - `FileUpload.vue` - File upload handling
  - `ImageCard.vue` - Image card display
  - `PlatformIndicator.vue` - Platform detection
  - `ThemeToggle.vue` - Light/dark theme toggle
  - `VaultUnlock.vue` - Vault access control
  
- **views/** - Page components
  - `DashboardView.vue` - Main dashboard
  - `HomeView.vue` - Home/landing page
  - `SettingsView.vue` - Settings page
  - `VaultView.vue` - Vault management view
  
- **stores/** - Pinia state management
  - `theme.ts` - Theme state management
  - `vault.ts` - Vault state management
  
- **router/** - Vue Router configuration
  - `index.ts` - Route definitions
  
- **types/** - TypeScript type definitions
  - `database.ts` - Database type interfaces
  - `tauri.ts` - Tauri API type interfaces
  
- **utils/** - Utility functions
  - `platform.ts` - Platform-specific utilities
  - `tauri.ts` - Tauri integration utilities

## Tauri Backend (src-tauri/)

- **src/** - Rust source files
  - `commands.rs` - Tauri command definitions
  - `database.rs` - Database operations
  - `encryption.rs` - Encryption utilities
  - `main.rs` - Main Rust entry point
  
- **icons/** - Application icons
- **Cargo.toml** - Rust dependencies
- **tauri.conf.json** - Tauri configuration

## Python Backend (python_backend/)

- **core/** - Core functionality
  - `core_engine.py` - Main engine
  - `session_manager.py` - Session handling
  - `vault_manager.py` - Vault operations
  
- **crypto/** - Encryption services
  - `crypto_controller.py` - Encryption controller
  - `decrypt.py` - Decryption functions
  - `encrypt.py` - Encryption functions
  
- **database/** - Database operations
  - `database_init.py` - Database initialization
  - `search_engine.py` - Search functionality
  
- **ipc/** - Inter-process communication
  - `ipc_gateway.py` - IPC gateway
  
- **storage/** - Storage operations
  - `storage_interface.py` - Storage interface
  
- **ui/** - UI-related functionality
  - `image_processor.py` - Image processing
  - `thumbnail.py` - Thumbnail generation
  
- **utils/** - Utility functions
  - `audit_logger.py` - Logging functionality
  - `tag_manager.py` - Tag management
  
- **tools/** - Development tools
  - **diagnostics/** - Diagnostic tools
  - **tests/** - Test scripts

## Test Vault (test_vault/)

The test vault provides a sandbox environment for development and testing:

- **data/** - Storage for encrypted files
- **database/** - SQLite database file
- **metadata/** - Metadata storage
- **backups/** - Backup directory
- **temp/** - Temporary file storage
- **thumbnails/** - Generated thumbnails
- **audit.log** - Audit log for actions
- **vault.config** - Vault configuration
- **vault.key** - Encryption key

## Utility Scripts

- **setup.bat** - Initial setup script for Windows
- **cleanup.bat** - Cleans temporary files and caches
