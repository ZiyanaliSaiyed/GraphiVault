use serde::{Deserialize, Serialize};
use tauri::AppHandle;
use uuid::Uuid;
use chrono::{DateTime, Utc};
use std::path::PathBuf;

#[derive(Debug, Serialize, Deserialize)]
pub struct ImageRecord {
    pub id: String,
    pub name: String,
    pub path: String,
    pub size: i64,
    pub mime_type: String,
    pub date_added: DateTime<Utc>,
    pub date_modified: DateTime<Utc>,
    pub tags: Vec<String>,
    pub metadata: serde_json::Value,
    pub is_encrypted: bool,
    pub thumbnail_path: Option<String>,
}

#[tauri::command]
pub async fn get_app_data_dir(app_handle: AppHandle) -> Result<String, String> {
    let app_data_dir = app_handle
        .path_resolver()
        .app_data_dir()
        .ok_or("Failed to get app data directory")?;
    
    Ok(app_data_dir.to_string_lossy().to_string())
}

#[tauri::command]
pub async fn init_database(app_handle: AppHandle) -> Result<(), String> {
    crate::database::init_db(&app_handle)
        .await
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn add_image(
    app_handle: AppHandle,
    name: String,
    path: String,
    size: i64,
    mime_type: String,
    tags: Vec<String>,
    metadata: serde_json::Value,
) -> Result<ImageRecord, String> {
    let id = Uuid::new_v4().to_string();
    let now = Utc::now();
    
    let image_record = ImageRecord {
        id: id.clone(),
        name,
        path,
        size,
        mime_type,
        date_added: now,
        date_modified: now,
        tags,
        metadata,
        is_encrypted: false,
        thumbnail_path: None,
    };
    
    crate::database::insert_image(&app_handle, &image_record)
        .await
        .map_err(|e| e.to_string())?;
    
    Ok(image_record)
}

#[tauri::command]
pub async fn get_images(app_handle: AppHandle) -> Result<Vec<ImageRecord>, String> {
    crate::database::get_all_images(&app_handle)
        .await
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn delete_image(app_handle: AppHandle, id: String) -> Result<(), String> {
    crate::database::delete_image(&app_handle, &id)
        .await
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn encrypt_file(
    app_handle: AppHandle,
    file_path: String,
    password: String,
) -> Result<String, String> {
    crate::encryption::encrypt_file(&file_path, &password)
        .await
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn decrypt_file(
    app_handle: AppHandle,
    encrypted_file_path: String,
    password: String,
    output_path: String,
) -> Result<(), String> {
    crate::encryption::decrypt_file(&encrypted_file_path, &password, &output_path)
        .await
        .map_err(|e| e.to_string())
}
