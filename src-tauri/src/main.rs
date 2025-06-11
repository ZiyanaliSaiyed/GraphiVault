// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod commands;
mod database;
mod encryption;

use tauri::{Manager, SystemTray, SystemTrayEvent, SystemTrayMenu, CustomMenuItem};

fn main() {
    // Create system tray
    let quit = CustomMenuItem::new("quit".to_string(), "Quit");
    let show = CustomMenuItem::new("show".to_string(), "Show");
    let tray_menu = SystemTrayMenu::new()
        .add_item(show)
        .add_separator()
        .add_item(quit);
    
    let system_tray = SystemTray::new().with_menu(tray_menu);

    tauri::Builder::default()
        .system_tray(system_tray)
        .on_system_tray_event(|app, event| match event {
            SystemTrayEvent::LeftClick {
                position: _,
                size: _,
                ..
            } => {
                let window = app.get_window("main").unwrap();
                window.show().unwrap();
                window.set_focus().unwrap();
            }
            SystemTrayEvent::MenuItemClick { id, .. } => match id.as_str() {
                "quit" => {
                    std::process::exit(0);
                }
                "show" => {
                    let window = app.get_window("main").unwrap();
                    window.show().unwrap();
                    window.set_focus().unwrap();
                }
                _ => {}
            },
            _ => {}        })        .invoke_handler(tauri::generate_handler![
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
            commands::unlock_vault,
            commands::lock_vault,
            commands::process_image_file,
            commands::search_images,
            commands::get_decrypted_image,
            commands::get_image_thumbnail
        ])
        .setup(|app| {
            // Initialize database on startup
            let app_handle = app.handle();
            tauri::async_runtime::spawn(async move {
                if let Err(e) = database::init_db(&app_handle).await {
                    eprintln!("Failed to initialize database: {}", e);
                }
            });
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
