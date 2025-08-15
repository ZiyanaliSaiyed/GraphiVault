use chrono::Utc;
use serde::{Deserialize, Serialize};
use sqlx::SqlitePool;
use std::collections::HashMap;
use tauri::State;

// Re-export database models
pub use crate::database::{AnnotationRecord, ImageRecord, TagRecord};

#[derive(Debug, Serialize, Deserialize)]
pub struct PythonBackendResponse {
    pub success: bool,
    pub data: Option<serde_json::Value>,
    pub error: Option<String>,
}

// Python backend integration helper
async fn call_python_backend(
    app_handle: &tauri::AppHandle,
    method: &str,
    args: &HashMap<String, serde_json::Value>,
) -> Result<PythonBackendResponse, String> {
    let _app_data_dir = app_handle
        .path_resolver()
        .app_data_dir()
        .ok_or("Failed to get app data directory")?;

    // Use test vault for now
    let vault_path = std::path::PathBuf::from("D:\\GraphiVault\\test_vault");

    // In development, look for python_backend in the project root
    // In production, look for it in the resource directory
    let python_backend_path = if cfg!(debug_assertions) {
        // Development mode - find project root by looking for package.json
        let mut current_dir = std::env::current_dir().unwrap();

        // Look for project root (contains package.json and python_backend)
        loop {
            let package_json = current_dir.join("package.json");
            let python_backend = current_dir.join("python_backend");

            if package_json.exists() && python_backend.exists() {
                break current_dir.join("python_backend");
            }

            match current_dir.parent() {
                Some(parent) => current_dir = parent.to_path_buf(),
                None => {
                    // Fallback to absolute path if we can't find project root
                    break std::path::PathBuf::from("D:\\GraphiVault\\python_backend");
                }
            }
        }
    } else {
        // Production mode - look in resource directory
        app_handle
            .path_resolver()
            .resource_dir()
            .unwrap_or_else(|| std::env::current_dir().unwrap())
            .join("python_backend")
    };

    // Prepare arguments
    let mut cmd_args = vec![
        python_backend_path
            .join("main.py")
            .to_string_lossy()
            .to_string(),
        method.to_string(), // Command as positional argument
        "--vault-path".to_string(),
        vault_path.to_string_lossy().to_string(),
    ];

    for (key, value) in args {
        cmd_args.push(format!("--{}", key));
        cmd_args.push(value.to_string().trim_matches('"').to_string());
    }

    // Debug logging for path resolution
    println!("🐍 Python backend path: {:?}", python_backend_path);
    println!("🐍 Main.py path: {:?}", python_backend_path.join("main.py"));
    println!("🐍 Command args: {:?}", cmd_args);

    let output = std::process::Command::new("python")
        .args(&cmd_args)
        .output()
        .map_err(|e| format!("Failed to execute Python backend: {}", e))?;

    let stdout = String::from_utf8_lossy(&output.stdout);
    let stderr = String::from_utf8_lossy(&output.stderr);

    // Enhanced debug logging
    println!("🐍 Python exit code: {:?}", output.status.code());
    println!("🐍 Python stdout: {}", stdout);
    println!("🐍 Python stderr: {}", stderr);

    if !output.status.success() {
        return Err(format!("Python backend error: {}", stderr));
    }

    if stdout.trim().is_empty() {
        return Err(format!(
            "Python backend returned empty response. stderr: {}",
            stderr
        ));
    }

    serde_json::from_str(&stdout).map_err(|e| {
        format!(
            "Failed to parse Python backend response: {}. Raw output: {}",
            e, stdout
        )
    })
}

#[tauri::command]
pub async fn get_app_data_dir(app_handle: tauri::AppHandle) -> Result<String, String> {
    let app_data_dir = app_handle
        .path_resolver()
        .app_data_dir()
        .ok_or("Failed to get app data directory")?;

    Ok(app_data_dir.to_string_lossy().to_string())
}

#[tauri::command]
pub async fn init_database(db: State<'_, SqlitePool>) -> Result<(), String> {
    crate::database::init_db(&db)
        .await
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn add_image(
    db: State<'_, SqlitePool>,
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
    let image_id = crate::database::insert_image(&db, &image_record)
        .await
        .map_err(|e| e.to_string())?;

    // Log the event
    crate::database::log_auth_event(
        &db,
        "image_added",
        "success",
        Some(&format!("Image ID: {}", image_id)),
    )
    .await
    .map_err(|e| e.to_string())?;

    Ok(image_id)
}

#[tauri::command]
pub async fn get_images(db: State<'_, SqlitePool>) -> Result<Vec<ImageRecord>, String> {
    crate::database::get_all_images(&db)
        .await
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn get_image_by_id(
    db: State<'_, SqlitePool>,
    id: i64,
) -> Result<Option<ImageRecord>, String> {
    crate::database::get_image_by_id(&db, id)
        .await
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn get_image_by_hash(
    db: State<'_, SqlitePool>,
    file_hash: String,
) -> Result<Option<ImageRecord>, String> {
    crate::database::get_image_by_hash(&db, &file_hash)
        .await
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn delete_image(db: State<'_, SqlitePool>, id: i64) -> Result<(), String> {
    crate::database::soft_delete_image(&db, id)
        .await
        .map_err(|e| e.to_string())?;
    // Log the event
    crate::database::log_auth_event(
        &db,
        "image_deleted",
        "success",
        Some(&format!("Image ID: {}", id)),
    )
    .await
    .map_err(|e| e.to_string())?;
    Ok(())
}

#[tauri::command]
pub async fn add_tag(
    db: State<'_, SqlitePool>,
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
    crate::database::insert_tag(&db, &tag_record)
        .await
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn get_image_tags(
    db: State<'_, SqlitePool>,
    image_id: i64,
) -> Result<Vec<TagRecord>, String> {
    crate::database::get_image_tags(&db, image_id)
        .await
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn add_annotation(
    db: State<'_, SqlitePool>,
    image_id: i64,
    note: String,
) -> Result<i64, String> {
    let annotation_record = AnnotationRecord {
        id: 0, // Will be auto-generated
        image_id,
        note,
        created_at: Utc::now().to_rfc3339(),
    };
    crate::database::insert_annotation(&db, &annotation_record)
        .await
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn get_image_annotations(
    db: State<'_, SqlitePool>,
    image_id: i64,
) -> Result<Vec<AnnotationRecord>, String> {
    crate::database::get_image_annotations(&db, image_id)
        .await
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn set_vault_setting(
    db: State<'_, SqlitePool>,
    key: String,
    value: String,
) -> Result<(), String> {
    crate::database::set_vault_meta(&db, &key, &value)
        .await
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn get_vault_setting(
    db: State<'_, SqlitePool>,
    key: String,
) -> Result<Option<String>, String> {
    crate::database::get_vault_meta(&db, &key)
        .await
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn get_vault_info(db: State<'_, SqlitePool>) -> Result<serde_json::Value, String> {
    let vault_id = crate::database::get_vault_meta(&db, "vault_id")
        .await
        .map_err(|e| e.to_string())?;
    let created_at = crate::database::get_vault_meta(&db, "created_at")
        .await
        .map_err(|e| e.to_string())?;
    let schema_version = crate::database::get_vault_meta(&db, "schema_version")
        .await
        .map_err(|e| e.to_string())?;
    // Get image count
    let images = crate::database::get_all_images(&db)
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
pub async fn encrypt_file(file_path: String, password: String) -> Result<String, String> {
    crate::encryption::encrypt_file(&file_path, &password)
        .await
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn decrypt_file(
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
    app_handle: tauri::AppHandle,
    master_password: String,
) -> Result<PythonBackendResponse, String> {
    let mut args = HashMap::new();
    args.insert(
        "password".to_string(),
        serde_json::Value::String(master_password),
    );

    call_python_backend(&app_handle, "initialize", &args).await
}

#[tauri::command]
pub async fn unlock_vault(
    app_handle: tauri::AppHandle,
    master_password: String,
) -> Result<PythonBackendResponse, String> {
    let mut args = HashMap::new();
    args.insert(
        "password".to_string(),
        serde_json::Value::String(master_password),
    );

    call_python_backend(&app_handle, "unlock", &args).await
}

#[tauri::command]
pub async fn lock_vault(app_handle: tauri::AppHandle) -> Result<PythonBackendResponse, String> {
    let args = HashMap::new();
    call_python_backend(&app_handle, "lock", &args).await
}

#[tauri::command]
pub async fn add_image_from_frontend(
    app_handle: tauri::AppHandle,
    file_contents: String, // Expecting base64 encoded file
    tags: Vec<String>,
    password: Option<String>, // Add optional password parameter
) -> Result<PythonBackendResponse, String> {
    let mut args = HashMap::new();
    args.insert(
        "file_contents".to_string(),
        serde_json::Value::String(file_contents),
    );
    args.insert(
        "tags".to_string(),
        serde_json::Value::String(
            serde_json::to_string(&tags).unwrap_or_else(|_| "[]".to_string()),
        ),
    );

    // Add password if provided
    if let Some(pwd) = password {
        args.insert("password".to_string(), serde_json::Value::String(pwd));
    }

    call_python_backend(&app_handle, "add_image", &args).await
}

#[tauri::command]
pub async fn search_images(
    app_handle: tauri::AppHandle,
    query: String,
    tags: Vec<String>,
) -> Result<PythonBackendResponse, String> {
    let mut args = HashMap::new();
    args.insert("query".to_string(), serde_json::Value::String(query));
    args.insert(
        "tags".to_string(),
        serde_json::Value::String(
            serde_json::to_string(&tags).unwrap_or_else(|_| "[]".to_string()),
        ),
    );

    call_python_backend(&app_handle, "search_images", &args).await
}

#[tauri::command]
pub async fn get_decrypted_image(
    app_handle: tauri::AppHandle,
    image_id: i64,
) -> Result<PythonBackendResponse, String> {
    let mut args = HashMap::new();
    args.insert(
        "image-id".to_string(),
        serde_json::Value::String(image_id.to_string()),
    );
    args.insert("decrypt".to_string(), serde_json::Value::Bool(true));

    call_python_backend(&app_handle, "get_image", &args).await
}

#[tauri::command]
pub async fn get_image_thumbnail(
    app_handle: tauri::AppHandle,
    image_id: i64,
) -> Result<PythonBackendResponse, String> {
    let mut args = HashMap::new();
    args.insert(
        "image-id".to_string(),
        serde_json::Value::String(image_id.to_string()),
    );

    call_python_backend(&app_handle, "get_image", &args).await
}

#[tauri::command]
pub async fn get_vault_status(
    app_handle: tauri::AppHandle,
) -> Result<PythonBackendResponse, String> {
    let args = HashMap::new();
    call_python_backend(&app_handle, "get_vault_status", &args).await
}
