// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod commands;
mod database;
mod encryption;

use sqlx::SqlitePool;
use std::fs;
use tauri::{CustomMenuItem, Manager, SystemTray, SystemTrayMenu};

fn main() {
    // Create system tray
    let quit = CustomMenuItem::new("quit".to_string(), "Quit");
    let show = CustomMenuItem::new("show".to_string(), "Show");
    let tray_menu = SystemTrayMenu::new().add_item(show).add_item(quit);
    let system_tray = SystemTray::new().with_menu(tray_menu);

    tauri::Builder::default()
        .system_tray(system_tray)
        .invoke_handler(tauri::generate_handler![
            commands::get_app_data_dir,
            commands::init_database,
            commands::add_image,
            commands::get_images,
            commands::get_image_by_id,
            commands::get_image_by_hash,
            commands::delete_image,
            commands::add_tag,
            commands::get_image_tags,
            commands::add_annotation,
            commands::get_image_annotations,
            commands::set_vault_setting,
            commands::get_vault_setting,
            commands::get_vault_info,
            commands::encrypt_file,
            commands::decrypt_file,
            commands::initialize_vault,
            commands::get_vault_status,
            commands::unlock_vault,
            commands::lock_vault,
            commands::add_image_from_frontend,
            commands::search_images,
            commands::get_decrypted_image,
            commands::get_image_thumbnail
        ])
        .setup(|app| {
            // Initialize database on startup and register pool as state
            let app_handle = app.handle();
            let app_data_dir = app_handle
                .path_resolver()
                .app_data_dir()
                .ok_or("Failed to get app data directory")?;
            println!("App data directory: {}", app_data_dir.display());

            fs::create_dir_all(&app_data_dir)?;
            let vault_dir = app_data_dir.join("vault");
            fs::create_dir_all(&vault_dir)?;
            fs::create_dir_all(vault_dir.join("data"))?;
            fs::create_dir_all(vault_dir.join("encrypted"))?;
            fs::create_dir_all(vault_dir.join("thumbnails"))?;
            fs::create_dir_all(vault_dir.join("temp"))?;
            fs::create_dir_all(vault_dir.join("backups"))?;

            // Try to use a shorter path to avoid Windows path length issues
            let db_path = vault_dir.join("vault.db");
            println!("Database path: {}", db_path.display());

            // Test if we can write to this location
            let test_file = vault_dir.join("test_write.tmp");
            match std::fs::write(&test_file, "test") {
                Ok(_) => {
                    println!("Write test successful");
                    let _ = std::fs::remove_file(&test_file);
                }
                Err(e) => {
                    println!("Write test failed: {}", e);
                    return Err(format!("Cannot write to vault directory: {}", e).into());
                }
            }

            // Ensure the database directory is writable
            let db_dir = db_path.parent().unwrap();
            if !db_dir.exists() {
                fs::create_dir_all(db_dir)?;
            }

            // Use a more compatible SQLite URL format with supported options
            // Convert Windows backslashes to forward slashes for SQLite URL
            let db_path_str = db_path.to_string_lossy().replace('\\', "/");
            let database_url = format!("sqlite:{}?mode=rwc", db_path_str);
            println!("Database URL: {}", database_url);

            let rt = tokio::runtime::Runtime::new()
                .map_err(|e| format!("Failed to create tokio runtime: {}", e))?;

            let pool = rt
                .block_on(SqlitePool::connect(&database_url))
                .map_err(|e| format!("Failed to connect to database: {}", e))?;

            // Initialize the database schema
            rt.block_on(crate::database::init_db(&pool))
                .map_err(|e| format!("Failed to initialize database: {}", e))?;

            println!("Database initialized successfully");
            app.manage(pool);
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
