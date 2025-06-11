use sqlx::{Row, SqlitePool};
use tauri::AppHandle;
use anyhow::Result;
use std::fs;
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

// GraphiVault Database Models
#[derive(Debug, Serialize, Deserialize, sqlx::FromRow)]
pub struct ImageRecord {
    pub id: i64,
    pub file_hash: String,
    pub file_name: String,  // Encrypted filename
    pub storage_path: String,  // Vault-relative path
    pub created_at: String,
    pub updated_at: String,
    pub file_size: i64,
    pub is_deleted: bool,
}

#[derive(Debug, Serialize, Deserialize, sqlx::FromRow)]
pub struct TagRecord {
    pub id: i64,
    pub image_id: i64,
    pub tag_name: String,  // Encrypted tag
    pub tag_type: Option<String>,
    pub created_at: String,
}

#[derive(Debug, Serialize, Deserialize, sqlx::FromRow)]
pub struct AnnotationRecord {
    pub id: i64,
    pub image_id: i64,
    pub note: String,  // Encrypted note
    pub created_at: String,
}

pub async fn init_db(app_handle: &AppHandle) -> Result<()> {
    let app_data_dir = app_handle
        .path_resolver()
        .app_data_dir()
        .ok_or_else(|| anyhow::anyhow!("Failed to get app data directory"))?;
    
    // Create GraphiVault directory structure
    fs::create_dir_all(&app_data_dir)?;
    let vault_dir = app_data_dir.join("vault");
    fs::create_dir_all(&vault_dir)?;
    fs::create_dir_all(vault_dir.join("data"))?;
    fs::create_dir_all(vault_dir.join("encrypted"))?;
    fs::create_dir_all(vault_dir.join("thumbnails"))?;
    fs::create_dir_all(vault_dir.join("temp"))?;
    fs::create_dir_all(vault_dir.join("backups"))?;
    
    let db_path = vault_dir.join("data").join("graphivault.db");
    let database_url = format!("sqlite:{}", db_path.to_string_lossy());
    
    let pool = SqlitePool::connect(&database_url).await?;
    
    // Configure SQLite for optimal security and performance
    sqlx::query("PRAGMA foreign_keys = ON").execute(&pool).await?;
    sqlx::query("PRAGMA journal_mode = WAL").execute(&pool).await?;
    sqlx::query("PRAGMA synchronous = NORMAL").execute(&pool).await?;
    sqlx::query("PRAGMA secure_delete = ON").execute(&pool).await?;
    sqlx::query("PRAGMA auto_vacuum = INCREMENTAL").execute(&pool).await?;
    sqlx::query("PRAGMA page_size = 4096").execute(&pool).await?;
    sqlx::query("PRAGMA cache_size = -64000").execute(&pool).await?; // 64MB cache
    sqlx::query("PRAGMA temp_store = MEMORY").execute(&pool).await?;
    
    // Create images table - core metadata for each image file
    sqlx::query(
        r#"
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_hash TEXT NOT NULL UNIQUE,
            file_name TEXT NOT NULL,
            storage_path TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            is_deleted BOOLEAN NOT NULL DEFAULT 0
        )
        "#,
    )
    .execute(&pool)
    .await?;
    
    // Create tags table - encrypted user-defined tags
    sqlx::query(
        r#"
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_id INTEGER NOT NULL,
            tag_name TEXT NOT NULL,
            tag_type TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE
        )
        "#,
    )
    .execute(&pool)
    .await?;
    
    // Create annotations table - encrypted notes/descriptions
    sqlx::query(
        r#"
        CREATE TABLE IF NOT EXISTS annotations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_id INTEGER NOT NULL,
            note TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE
        )
        "#,
    )
    .execute(&pool)
    .await?;
    
    // Create vault_meta table - vault-level config and settings
    sqlx::query(
        r#"
        CREATE TABLE IF NOT EXISTS vault_meta (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            last_updated TEXT NOT NULL
        )
        "#,
    )
    .execute(&pool)
    .await?;
    
    // Create auth_logs table - access attempts and critical operations
    sqlx::query(
        r#"
        CREATE TABLE IF NOT EXISTS auth_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            status TEXT NOT NULL,
            details TEXT
        )
        "#,
    )
    .execute(&pool)
    .await?;
    
    // Create performance indexes
    sqlx::query("CREATE INDEX IF NOT EXISTS idx_images_file_hash ON images(file_hash)").execute(&pool).await?;
    sqlx::query("CREATE INDEX IF NOT EXISTS idx_images_created_at ON images(created_at)").execute(&pool).await?;
    sqlx::query("CREATE INDEX IF NOT EXISTS idx_images_updated_at ON images(updated_at)").execute(&pool).await?;
    sqlx::query("CREATE INDEX IF NOT EXISTS idx_images_storage_path ON images(storage_path)").execute(&pool).await?;
    sqlx::query("CREATE INDEX IF NOT EXISTS idx_tags_image_id ON tags(image_id)").execute(&pool).await?;
    sqlx::query("CREATE INDEX IF NOT EXISTS idx_tags_created_at ON tags(created_at)").execute(&pool).await?;
    sqlx::query("CREATE INDEX IF NOT EXISTS idx_annotations_image_id ON annotations(image_id)").execute(&pool).await?;
    sqlx::query("CREATE INDEX IF NOT EXISTS idx_auth_logs_timestamp ON auth_logs(timestamp)").execute(&pool).await?;
    sqlx::query("CREATE INDEX IF NOT EXISTS idx_auth_logs_event_type ON auth_logs(event_type)").execute(&pool).await?;
    
    // Initialize vault metadata if not exists
    let count: (i64,) = sqlx::query_as("SELECT COUNT(*) FROM vault_meta WHERE key = 'schema_version'")
        .fetch_one(&pool)
        .await?;
    
    if count.0 == 0 {
        let now = Utc::now().to_rfc3339();
        let vault_id = uuid::Uuid::new_v4().to_string();
        
        sqlx::query("INSERT INTO vault_meta (key, value, last_updated) VALUES (?, ?, ?)")
            .bind("schema_version")
            .bind("1")
            .bind(&now)
            .execute(&pool)
            .await?;
            
        sqlx::query("INSERT INTO vault_meta (key, value, last_updated) VALUES (?, ?, ?)")
            .bind("vault_id")
            .bind(&vault_id)
            .bind(&now)
            .execute(&pool)
            .await?;
            
        sqlx::query("INSERT INTO vault_meta (key, value, last_updated) VALUES (?, ?, ?)")
            .bind("created_at")
            .bind(&now)
            .bind(&now)
            .execute(&pool)
            .await?;
    }
    
    // Store the pool in app state
    app_handle.manage(pool);
    
    Ok(())
}

pub async fn insert_image(app_handle: &AppHandle, image: &ImageRecord) -> Result<i64> {
    let pool = app_handle.state::<SqlitePool>();
    
    let result = sqlx::query(
        r#"
        INSERT INTO images (
            file_hash, file_name, storage_path, created_at, updated_at, file_size, is_deleted
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        "#,
    )
    .bind(&image.file_hash)
    .bind(&image.file_name)
    .bind(&image.storage_path)
    .bind(&image.created_at)
    .bind(&image.updated_at)
    .bind(image.file_size)
    .bind(image.is_deleted)
    .execute(&**pool)
    .await?;
    
    Ok(result.last_insert_rowid())
}

pub async fn get_all_images(app_handle: &AppHandle) -> Result<Vec<ImageRecord>> {
    let pool = app_handle.state::<SqlitePool>();
    
    let images = sqlx::query_as::<_, ImageRecord>(
        "SELECT id, file_hash, file_name, storage_path, created_at, updated_at, file_size, is_deleted FROM images WHERE is_deleted = 0 ORDER BY created_at DESC"
    )
    .fetch_all(&**pool)
    .await?;
    
    Ok(images)
}

pub async fn get_image_by_id(app_handle: &AppHandle, id: i64) -> Result<Option<ImageRecord>> {
    let pool = app_handle.state::<SqlitePool>();
    
    let image = sqlx::query_as::<_, ImageRecord>(
        "SELECT id, file_hash, file_name, storage_path, created_at, updated_at, file_size, is_deleted FROM images WHERE id = ? AND is_deleted = 0"
    )
    .bind(id)
    .fetch_optional(&**pool)
    .await?;
    
    Ok(image)
}

pub async fn get_image_by_hash(app_handle: &AppHandle, file_hash: &str) -> Result<Option<ImageRecord>> {
    let pool = app_handle.state::<SqlitePool>();
    
    let image = sqlx::query_as::<_, ImageRecord>(
        "SELECT id, file_hash, file_name, storage_path, created_at, updated_at, file_size, is_deleted FROM images WHERE file_hash = ? AND is_deleted = 0"
    )
    .bind(file_hash)
    .fetch_optional(&**pool)
    .await?;
    
    Ok(image)
}

pub async fn soft_delete_image(app_handle: &AppHandle, id: i64) -> Result<()> {
    let pool = app_handle.state::<SqlitePool>();
    
    let now = Utc::now().to_rfc3339();
    
    sqlx::query("UPDATE images SET is_deleted = 1, updated_at = ? WHERE id = ?")
        .bind(&now)
        .bind(id)
        .execute(&**pool)
        .await?;
    
    Ok(())
}

pub async fn insert_tag(app_handle: &AppHandle, tag: &TagRecord) -> Result<i64> {
    let pool = app_handle.state::<SqlitePool>();
    
    let result = sqlx::query(
        "INSERT INTO tags (image_id, tag_name, tag_type, created_at) VALUES (?, ?, ?, ?)"
    )
    .bind(tag.image_id)
    .bind(&tag.tag_name)
    .bind(&tag.tag_type)
    .bind(&tag.created_at)
    .execute(&**pool)
    .await?;
    
    Ok(result.last_insert_rowid())
}

pub async fn get_image_tags(app_handle: &AppHandle, image_id: i64) -> Result<Vec<TagRecord>> {
    let pool = app_handle.state::<SqlitePool>();
    
    let tags = sqlx::query_as::<_, TagRecord>(
        "SELECT id, image_id, tag_name, tag_type, created_at FROM tags WHERE image_id = ? ORDER BY created_at"
    )
    .bind(image_id)
    .fetch_all(&**pool)
    .await?;
    
    Ok(tags)
}

pub async fn insert_annotation(app_handle: &AppHandle, annotation: &AnnotationRecord) -> Result<i64> {
    let pool = app_handle.state::<SqlitePool>();
    
    let result = sqlx::query(
        "INSERT INTO annotations (image_id, note, created_at) VALUES (?, ?, ?)"
    )
    .bind(annotation.image_id)
    .bind(&annotation.note)
    .bind(&annotation.created_at)
    .execute(&**pool)
    .await?;
    
    Ok(result.last_insert_rowid())
}

pub async fn get_image_annotations(app_handle: &AppHandle, image_id: i64) -> Result<Vec<AnnotationRecord>> {
    let pool = app_handle.state::<SqlitePool>();
    
    let annotations = sqlx::query_as::<_, AnnotationRecord>(
        "SELECT id, image_id, note, created_at FROM annotations WHERE image_id = ? ORDER BY created_at"
    )
    .bind(image_id)
    .fetch_all(&**pool)
    .await?;
    
    Ok(annotations)
}

pub async fn set_vault_meta(app_handle: &AppHandle, key: &str, value: &str) -> Result<()> {
    let pool = app_handle.state::<SqlitePool>();
    
    let now = Utc::now().to_rfc3339();
    
    sqlx::query("INSERT OR REPLACE INTO vault_meta (key, value, last_updated) VALUES (?, ?, ?)")
        .bind(key)
        .bind(value)
        .bind(&now)
        .execute(&**pool)
        .await?;
    
    Ok(())
}

pub async fn get_vault_meta(app_handle: &AppHandle, key: &str) -> Result<Option<String>> {
    let pool = app_handle.state::<SqlitePool>();
    
    let result: Option<(String,)> = sqlx::query_as("SELECT value FROM vault_meta WHERE key = ?")
        .bind(key)
        .fetch_optional(&**pool)
        .await?;
    
    Ok(result.map(|r| r.0))
}

pub async fn log_auth_event(app_handle: &AppHandle, event_type: &str, status: &str, details: Option<&str>) -> Result<()> {
    let pool = app_handle.state::<SqlitePool>();
    
    let now = Utc::now().to_rfc3339();
    
    sqlx::query("INSERT INTO auth_logs (event_type, timestamp, status, details) VALUES (?, ?, ?, ?)")
        .bind(event_type)
        .bind(&now)
        .bind(status)
        .bind(details)
        .execute(&**pool)
        .await?;
    
    Ok(())
}
