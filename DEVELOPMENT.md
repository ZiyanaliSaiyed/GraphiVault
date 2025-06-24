# GraphiVault Development Guide

## Prerequisites

Make sure you have the following installed:

- **Node.js** (v18 or higher)
- **Rust** (v1.70 or higher)
- **Python** (v3.8 or higher)

## Quick Setup

1. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Tauri CLI (if not already installed):**
   ```bash
   npm install -g @tauri-apps/cli
   ```

## Development Commands

### Start Development Server
```bash
npm run tauri:dev
```
This will start both the frontend development server and the Tauri application.

### Frontend Only (for UI development)
```bash
npm run dev
```

### Build for Production
```bash
npm run tauri:build
```

### Linting and Formatting
```bash
npm run lint
npm run format
```

## Project Structure

```
GraphiVault/
├── src/                    # Vue.js frontend
│   ├── components/         # Reusable Vue components
│   ├── views/              # Page components
│   ├── stores/             # Pinia state management
│   ├── utils/              # Utility functions
│   └── types/              # TypeScript type definitions
├── src-tauri/              # Rust backend
│   └── src/                # Rust source code
├── python_backend/         # Python backend
│   ├── core/               # Core functionality
│   ├── crypto/             # Encryption functionality
│   ├── database/           # Database operations
│   ├── ipc/                # Inter-process communication
│   ├── storage/            # Storage operations
│   ├── ui/                 # UI-related functionality
│   ├── utils/              # Utility functions
│   └── tools/              # Development tools
│       ├── diagnostics/    # Diagnostic tools
│       └── tests/          # Test scripts
└── test_vault/            # Test vault for development
```

## Key Features Implementation Status

### ✅ Completed
- [x] Project structure and configuration
- [x] Vue 3 + TypeScript frontend
- [x] Tauri Rust backend
- [x] Basic UI components and routing
- [x] Theme system (light/dark mode)
- [x] Python encryption backend
- [x] Database schema design

### 🚧 In Progress
- [ ] File upload and processing
- [ ] Image encryption/decryption
- [ ] Thumbnail generation
- [ ] Database integration
- [ ] Search and filtering

### 📋 Todo
- [ ] Image viewer
- [ ] Metadata editing
- [ ] Backup/restore
- [ ] Settings persistence
- [ ] Error handling
- [ ] Testing suite

## Development Tips

1. **VS Code Extensions**: Install the recommended extensions for the best development experience.

2. **Hot Reload**: The development server supports hot reload for both frontend and backend changes.

3. **Database**: SQLite database is automatically created in the app data directory.

4. **Python Scripts**: Located in `python_backend/` - these handle encryption and image processing.

5. **Debugging**: Use VS Code debugger or browser dev tools for frontend, and `println!` macros for Rust backend.

## Troubleshooting

### Common Issues

1. **Tauri build fails**: Make sure Rust is properly installed and updated.
2. **Python scripts fail**: Verify Python dependencies are installed.
3. **Frontend not loading**: Check if the development server is running on port 1420.

### Getting Help

- Check the [Tauri documentation](https://tauri.app/v1/guides/)
- Review [Vue 3 documentation](https://vuejs.org/guide/)
- Look at the GitHub issues for common problems
