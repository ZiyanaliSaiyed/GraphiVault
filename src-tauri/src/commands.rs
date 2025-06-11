use serde::{Deserialize, Serialize};
use tauri::AppHandle;
use uuid::Uuid;
use chrono::{DateTime, Utc};
use std::path::PathBuf;
use std::process::Command;
use std::collections::HashMap;

// Re-export database models
pub use crate::database::{ImageRecord, TagRecord, AnnotationRecord};

#[derive(Debug, Serialize, Deserialize)]
pub struct PythonBackendResponse {
    pub success: bool,
    pub data: Option<serde_json::Value>,
    pub error: Option<String>,
}

// Python backend integration helper
async fn call_python_backend(
    app_handle: &AppHandle,
    method: &str,
    args: &HashMap<String, serde_json::Value>,
) -> Result<PythonBackendResponse, String> {
    let app_data_dir = app_handle
        .path_resolver()
        .app_data_dir()
        .ok_or("Failed to get app data directory")?;
    
    let vault_path = app_data_dir.join("vault");
    let python_backend_path = app_handle
        .path_resolver()
        .resource_dir()
        .unwrap_or_else(|| std::env::current_dir().unwrap())
        .join("python_backend");
    
    // Prepare arguments
    let mut cmd_args = vec![
        python_backend_path.join("main.py").to_string_lossy().to_string(),
        "--method".to_string(),
        method.to_string(),
        "--vault-path".to_string(),
        vault_path.to_string_lossy().to_string(),
    ];
    
    for (key, value) in args {
        cmd_args.push(format!("--{}", key));
        cmd_args.push(value.to_string().trim_matches('"').to_string());
    }
    
    let output = Command::new("python")
        .args(&cmd_args)
        .output()
        .map_err(|e| format!("Failed to execute Python backend: {}", e))?;
    
    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        return Err(format!("Python backend error: {}", stderr));
    }
    
    let stdout = String::from_utf8_lossy(&output.stdout);
    serde_json::from_str(&stdout)
        .map_err(|e| format!("Failed to parse Python backend response: {}", e))
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
    file_hash: String,
    file_name: String,
    storage_path: String,
    file_size: i64,
) -> Result<i64, String> {
    let now = Utc::now().to_rfc3339();
    
    let image_record = ImageRecord {
        id: 0, // Will be auto-generated
        file_hash,
        file_name,
        storage_path,
        created_at: now.clone(),
        updated_at: now,
        file_size,
        is_deleted: false,
    };
    
    let image_id = crate::database::insert_image(&app_handle, &image_record)
        .await
        .map_err(|e| e.to_string())?;
    
    // Log the event
    crate::database::log_auth_event(&app_handle, "image_added", "success", Some(&format!("Image ID: {}", image_id)))
        .await
        .map_err(|e| e.to_string())?;
    
    Ok(image_id)
}

#[tauri::command]
pub async fn get_images(app_handle: AppHandle) -> Result<Vec<ImageRecord>, String> {
    crate::database::get_all_images(&app_handle)
        .await
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn get_image_by_id(app_handle: AppHandle, id: i64) -> Result<Option<ImageRecord>, String> {
    crate::database::get_image_by_id(&app_handle, id)
        .await
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn get_image_by_hash(app_handle: AppHandle, file_hash: String) -> Result<Option<ImageRecord>, String> {
    crate::database::get_image_by_hash(&app_handle, &file_hash)
        .await
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn delete_image(app_handle: AppHandle, id: i64) -> Result<(), String> {
    crate::database::soft_delete_image(&app_handle, id)
        .await
        .map_err(|e| e.to_string())?;
    
    // Log the event
    crate::database::log_auth_event(&app_handle, "image_deleted", "success", Some(&format!("Image ID: {}", id)))
        .await
        .map_err(|e| e.to_string())?;
    
    Ok(())
}

#[tauri::command]
pub async fn add_tag(
    app_handle: AppHandle,
    image_id: i64,
    tag_name: String,
    tag_type: Option<String>,
) -> Result<i64, String> {
    let tag_record = TagRecord {
        id: 0, // Will be auto-generated
        image_id,
        tag_name,
        tag_type,
        created_at: Utc::now().to_rfc3339(),
    };
    
    crate::database::insert_tag(&app_handle, &tag_record)
        .await
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn get_image_tags(app_handle: AppHandle, image_id: i64) -> Result<Vec<TagRecord>, String> {
    crate::database::get_image_tags(&app_handle, image_id)
        .await
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn add_annotation(
    app_handle: AppHandle,
    image_id: i64,
    note: String,
) -> Result<i64, String> {
    let annotation_record = AnnotationRecord {
        id: 0, // Will be auto-generated
        image_id,
        note,
        created_at: Utc::now().to_rfc3339(),
    };
    
    crate::database::insert_annotation(&app_handle, &annotation_record)
        .await
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn get_image_annotations(app_handle: AppHandle, image_id: i64) -> Result<Vec<AnnotationRecord>, String> {
    crate::database::get_image_annotations(&app_handle, image_id)
        .await
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn set_vault_setting(app_handle: AppHandle, key: String, value: String) -> Result<(), String> {
    crate::database::set_vault_meta(&app_handle, &key, &value)
        .await
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn get_vault_setting(app_handle: AppHandle, key: String) -> Result<Option<String>, String> {
    crate::database::get_vault_meta(&app_handle, &key)
        .await
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn get_vault_info(app_handle: AppHandle) -> Result<serde_json::Value, String> {
    let vault_id = crate::database::get_vault_meta(&app_handle, "vault_id")
        .await
        .map_err(|e| e.to_string())?;
        
    let created_at = crate::database::get_vault_meta(&app_handle, "created_at")
        .await
        .map_err(|e| e.to_string())?;
        
    let schema_version = crate::database::get_vault_meta(&app_handle, "schema_version")
        .await
        .map_err(|e| e.to_string())?;
    
    // Get image count
    let images = crate::database::get_all_images(&app_handle)
        .await
        .map_err(|e| e.to_string())?;
    
    let vault_info = serde_json::json!({
        "vault_id": vault_id,
        "created_at": created_at,
        "schema_version": schema_version,
        "total_images": images.len(),
        "status": "active"
    });
    
    Ok(vault_info)
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

#[tauri::command]
pub async fn initialize_vault(
    app_handle: AppHandle,
    master_password: String,
) -> Result<PythonBackendResponse, String> {
    let mut args = HashMap::new();
    args.insert("master_password".to_string(), serde_json::Value::String(master_password));
    
    call_python_backend(&app_handle, "initialize_vault", &args).await
}

#[tauri::command]
pub async fn unlock_vault(
    app_handle: AppHandle,
    master_password: String,
) -> Result<PythonBackendResponse, String> {
    let mut args = HashMap::new();
    args.insert("master_password".to_string(), serde_json::Value::String(master_password));
    
    call_python_backend(&app_handle, "unlock_vault", &args).await
}

#[tauri::command]
pub async fn lock_vault(app_handle: AppHandle) -> Result<PythonBackendResponse, String> {
    let args = HashMap::new();
    call_python_backend(&app_handle, "lock_vault", &args).await
}

#[tauri::command]
pub async fn process_image_file(
    app_handle: AppHandle,
    file_path: String,
    tags: Vec<String>,
) -> Result<PythonBackendResponse, String> {
    let mut args = HashMap::new();
    args.insert("file_path".to_string(), serde_json::Value::String(file_path));
    args.insert("tags".to_string(), serde_json::Value::Array(
        tags.into_iter().map(serde_json::Value::String).collect()
    ));
    
    call_python_backend(&app_handle, "add_encrypted_image", &args).await
}

#[tauri::command]
pub async fn search_images(
    app_handle: AppHandle,
    query: String,
    tags: Vec<String>,
) -> Result<PythonBackendResponse, String> {
    let mut args = HashMap::new();
    args.insert("query".to_string(), serde_json::Value::String(query));
    args.insert("tags".to_string(), serde_json::Value::Array(
        tags.into_iter().map(serde_json::Value::String).collect()
    ));
    
    call_python_backend(&app_handle, "search_images", &args).await
}

#[tauri::command]
pub async fn get_decrypted_image(
    app_handle: AppHandle,
    image_id: i64,
) -> Result<PythonBackendResponse, String> {
    let mut args = HashMap::new();
    args.insert("image_id".to_string(), serde_json::Value::Number(serde_json::Number::from(image_id)));
    
    call_python_backend(&app_handle, "get_decrypted_image", &args).await
}

#[tauri::command]
pub async fn get_image_thumbnail(
    app_handle: AppHandle,
    image_id: i64,
) -> Result<PythonBackendResponse, String> {
    let mut args = HashMap::new();
    args.insert("image_id".to_string(), serde_json::Value::Number(serde_json::Number::from(image_id)));
    
    call_python_backend(&app_handle, "get_thumbnail", &args).await
}
